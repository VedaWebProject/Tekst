import json

from pathlib import Path as PathObj
from tempfile import NamedTemporaryFile
from typing import Annotated, Any
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import GTE, LTE, In
from fastapi import (
    APIRouter,
    Body,
    File,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import StringConstraints
from starlette.background import BackgroundTask

from tekst import errors, notifications, tasks
from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.config import ConfigDep, TekstConfig
from tekst.logs import log
from tekst.models.common import PrecomputedDataDocument
from tekst.models.content import ContentBaseDocument
from tekst.models.correction import CorrectionDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceCoverage,
    ResourceExportFormat,
    res_exp_fmt_info,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.resources import (
    AnyResourceCreate,
    AnyResourceRead,
    AnyResourceUpdate,
    call_resource_maintenance_hooks,
    get_resource_template_readme,
    resource_types_mgr,
)
from tekst.resources.text_annotation import AnnotationAggregation
from tekst.search import set_index_ood
from tekst.utils import pick_translation


async def preprocess_resource_read(
    resource_doc: ResourceBaseDocument,
    for_user: UserRead | None = None,
) -> AnyResourceRead:
    # convert resource document to resource type's read model instance
    resource = (
        resource_types_mgr.get(resource_doc.resource_type)
        .resource_model()
        .read_model()(
            **resource_doc.model_dump(exclude=resource_doc.restricted_fields(for_user))
        )
    )
    # include writable flag
    resource.writable = bool(
        for_user
        and (
            for_user.is_superuser
            or (
                (
                    for_user.id == resource.owner_id
                    or for_user.id in resource.shared_write
                )
                and not resource.public
                and not resource.proposed
            )
        )
    )
    # include owner user data in each resource model (if an owner id is set)
    if resource.owner_id:
        resource.owner = UserReadPublic.model_from(
            await UserDocument.get(resource.owner_id)
        )
    # include shared-with user data in each resource model (if any)
    if for_user and (for_user.is_superuser or for_user.id == resource.owner_id):
        if resource.shared_read:
            resource.shared_read_users = await UserDocument.find(
                In(UserDocument.id, resource.shared_read)
            ).to_list()
        if resource.shared_write:
            resource.shared_write_users = await UserDocument.find(
                In(UserDocument.id, resource.shared_write)
            ).to_list()
    # include corrections count if user is owner of the resource
    # or, if resource has no owner, user is superuser
    if for_user and (
        (resource.owner_id and for_user.id == resource.owner_id)
        or (not resource.owner_id and for_user.is_superuser)
    ):
        resource.corrections = await CorrectionDocument.find(
            CorrectionDocument.resource_id == resource.id
        ).count()
    return resource


router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)


@router.get(
    "/maintenance",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def trigger_resources_maintenance(
    su: SuperuserDep,
) -> tasks.TaskDocument:
    return await tasks.create_task(
        call_resource_maintenance_hooks,
        tasks.TaskType.RESOURCE_MAINTENANCE_HOOK,
        user_id=su.id,
    )


@router.post(
    "",
    response_model=AnyResourceRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_RESOURCES_LIMIT_REACHED,
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_400_RESOURCE_INVALID_LEVEL,
        ]
    ),
)
async def create_resource(
    resource: AnyResourceCreate, user: UserDep, cfg: ConfigDep
) -> AnyResourceRead:
    # check user resources limit
    if (
        not user.is_superuser
        and await ResourceBaseDocument.user_resource_count(user.id)
        >= cfg.misc.max_resources_per_user
    ):
        raise errors.E_409_RESOURCES_LIMIT_REACHED

    # check text integrity
    text = await TextDocument.get(resource.text_id)
    if not text:
        raise errors.E_400_INVALID_TEXT
    if resource.level > len(text.levels) - 1:
        raise errors.E_400_RESOURCE_INVALID_LEVEL

    # force some values on creation
    resource.owner_id = user.id
    resource.proposed = False
    resource.public = False
    resource.shared_read = []
    resource.shared_write = []

    # find document model for this resource type, instantiate, create
    resource_doc = (
        await resource_types_mgr.get(resource.resource_type)
        .resource_model()
        .document_model()
        .model_from(resource)
        .create()
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/version",
    response_model=AnyResourceRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_RESOURCES_LIMIT_REACHED,
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_RESOURCE_VERSION_OF_VERSION,
        ]
    ),
)
async def create_resource_version(
    user: UserDep,
    cfg: ConfigDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyResourceRead:
    # check user resources limit
    if (
        not user.is_superuser
        and await ResourceBaseDocument.user_resource_count(user.id)
        >= cfg.misc.max_resources_per_user
    ):
        raise errors.E_409_RESOURCES_LIMIT_REACHED

    # check if resource exists
    resource_doc: ResourceBaseDocument = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    # check if resource is already a version
    if resource_doc.original_id:
        raise errors.E_400_RESOURCE_VERSION_OF_VERSION

    # generate version title
    version_title_suffix = " v" + str(
        await ResourceBaseDocument.find(
            ResourceBaseDocument.original_id == resource_id,
            with_children=True,
        ).count()
        + 2
    )
    version_title = [
        {
            "locale": tt.get("locale", "*"),
            "translation": tt.get("translation", "")[0 : 64 - len(version_title_suffix)]
            + version_title_suffix,
        }
        for tt in resource_doc.title
    ]

    # create version
    version_doc = (
        await resource_types_mgr.get(resource_doc.resource_type)
        .resource_model()
        .document_model()
        .model_from(
            resource_doc.model_copy(
                update={
                    ResourceBaseDocument.id: None,
                    ResourceBaseDocument.title: version_title,
                    ResourceBaseDocument.original_id: resource_doc.id,
                    ResourceBaseDocument.owner_id: user.id,
                    ResourceBaseDocument.proposed: False,
                    ResourceBaseDocument.public: False,
                    ResourceBaseDocument.shared_read: [],
                    ResourceBaseDocument.shared_write: [],
                }
            )
        )
        .create()
    )
    return await preprocess_resource_read(version_doc, user)


@router.patch(
    "/{id}",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_SHARED_WITH_USER_NON_EXISTENT,
        ]
    ),
)
async def update_resource(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyResourceUpdate,
    user: UserDep,
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    # only allow shares modification for owner or superuser
    if not user.is_superuser and resource_doc.owner_id != user.id:
        updates.shared_read = resource_doc.shared_read
        updates.shared_write = resource_doc.shared_write
    # conditionally force certain updates
    if resource_doc.public:
        updates.shared_read = []
        updates.shared_write = []
    # if the updates contain user shares, check if they are valid
    if updates.shared_read or updates.shared_write:
        for user_id in (updates.shared_read or []) + (updates.shared_write or []):
            if not await UserDocument.find_one(UserDocument.id == user_id).exists():
                raise errors.E_400_SHARED_WITH_USER_NON_EXISTENT
    # update document
    await resource_doc.apply_updates(updates)
    return await preprocess_resource_read(resource_doc, user)


@router.get(
    "",
    response_model=list[AnyResourceRead],
    status_code=status.HTTP_200_OK,
)
async def find_resources(
    user: OptionalUserDep,
    text_id: Annotated[
        PydanticObjectId,
        Query(alias="txt", description="ID of text to find resources for"),
    ] = None,
    level: Annotated[
        int, Query(alias="lvl", description="Structure level to find resources for")
    ] = None,
    resource_type: Annotated[
        str,
        StringConstraints(min_length=1, max_length=32, strip_whitespace=True),
        Query(alias="type", description="Type of resources to find"),
    ] = None,
    limit: int = 4096,
) -> list[AnyResourceRead]:
    """
    Returns a list of all resources matching the given criteria.

    As the resulting list of resources may contain resources of different types, the
    returned resource objects cannot be typed to their precise resource type.
    """
    # construct search example
    example = {}
    if text_id is not None:
        example["text_id"] = text_id
    if level is not None:
        example["level"] = level
    if resource_type:
        example["resource_type"] = resource_type

    # query for resources the user is allowed to read and that belong to active texts
    resource_docs = (
        await ResourceBaseDocument.find(
            example,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )
    # return processed results
    return [
        await preprocess_resource_read(resource_doc, user)
        for resource_doc in resource_docs
    ]


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=AnyResourceRead,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_resource(
    user: OptionalUserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    return await preprocess_resource_read(resource_doc, user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
            errors.E_400_RESOURCE_PUBLIC_DELETE,
            errors.E_400_RESOURCE_PROPOSED_DELETE,
        ]
    ),
)
async def delete_resource(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(
            alias="id",
        ),
    ],
) -> None:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise errors.E_403_FORBIDDEN
    if resource_doc.public:
        raise errors.E_400_RESOURCE_PUBLIC_DELETE
    if resource_doc.proposed:
        raise errors.E_400_RESOURCE_PROPOSED_DELETE

    # all fine
    # turn versions of this resource into original resources
    await ResourceBaseDocument.find(
        ResourceBaseDocument.original_id == resource_id,
        with_children=True,
    ).set({ResourceBaseDocument.original_id: None})

    # delete contents belonging to the resource
    await ContentBaseDocument.find(
        ContentBaseDocument.resource_id == resource_id,
        with_children=True,
    ).delete()

    # delete correction notes belonging to the resource
    await CorrectionDocument.find(
        CorrectionDocument.resource_id == resource_id,
    ).delete()

    # mark the text's index as out-of-date
    await set_index_ood(
        resource_doc.text_id,
        by_public_resource=resource_doc.public,
    )

    # delete resource itself
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        with_children=True,
    ).delete()


@router.post(
    "/{id}/transfer",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_409_RESOURCES_LIMIT_REACHED,
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_RESOURCE_PUBLIC_PROPOSED_TRANSFER,
            errors.E_403_FORBIDDEN,
            errors.E_400_TARGET_USER_NON_EXISTENT,
        ]
    ),
)
async def transfer_resource(
    user: UserDep,
    cfg: ConfigDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    target_user_id: Annotated[PydanticObjectId, Body()],
) -> AnyResourceRead:
    # check if resource exists
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    # check if user is allowed to transfer resource
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise errors.E_403_FORBIDDEN
    if resource_doc.public or resource_doc.proposed:
        raise errors.E_400_RESOURCE_PUBLIC_PROPOSED_TRANSFER

    # check if target user exists
    target_user: UserDocument = await UserDocument.get(target_user_id)
    if not target_user:
        raise errors.E_400_TARGET_USER_NON_EXISTENT

    # if the target user is already the owner, return the resource
    if target_user_id == resource_doc.owner_id:
        return await preprocess_resource_read(resource_doc, user)

    # check user resources limit
    if (
        not target_user.is_superuser
        and await ResourceBaseDocument.user_resource_count(target_user_id)
        >= cfg.misc.max_resources_per_user
    ):
        raise errors.E_409_RESOURCES_LIMIT_REACHED  # pragma: no cover (a paint to test)

    # all fine, transfer resource and remove target user ID from resource shares
    await resource_doc.set(
        {
            ResourceBaseDocument.owner_id: target_user_id,
            ResourceBaseDocument.shared_read: [
                u_id
                for u_id in resource_doc.shared_read
                if str(u_id) != str(target_user_id)
            ],
            ResourceBaseDocument.shared_write: [
                u_id
                for u_id in resource_doc.shared_write
                if str(u_id) != str(target_user_id)
            ],
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/propose",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
            errors.E_400_RESOURCE_VERSION_PROPOSE,
        ]
    ),
)
async def propose_resource(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise errors.E_403_FORBIDDEN
    if resource_doc.proposed:
        return await preprocess_resource_read(resource_doc, user)
    if resource_doc.public:
        raise errors.E_400_RESOURCE_PROPOSE_PUBLIC
    if resource_doc.original_id:
        raise errors.E_400_RESOURCE_VERSION_PROPOSE
    # all fine, propose resource
    await resource_doc.set(
        {
            ResourceBaseDocument.proposed: True,
            ResourceBaseDocument.shared_read: [],
            ResourceBaseDocument.shared_write: [],
        }
    )
    # notify users about the new proposal
    await notifications.broadcast_user_notification(
        notifications.TemplateIdentifier.USRMSG_RESOURCE_PROPOSED,
        username=user.name if "name" in user.public_fields else user.username,
        resource_title=pick_translation(resource_doc.title),
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpropose",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def unpropose_resource(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise errors.E_403_FORBIDDEN
    # all fine, unpropose resource
    await resource_doc.set(
        {
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.public: False,
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/publish",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_RESOURCE_PUBLISH_UNPROPOSED,
            errors.E_400_RESOUCE_VERSION_PUBLISH,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def publish_resource(
    user: SuperuserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if resource_doc.public:
        return await preprocess_resource_read(resource_doc, user)
    if not resource_doc.proposed:
        raise errors.E_400_RESOURCE_PUBLISH_UNPROPOSED
    if resource_doc.original_id:
        raise errors.E_400_RESOUCE_VERSION_PUBLISH

    # all fine, publish resource
    await resource_doc.set(
        {
            ResourceBaseDocument.public: True,
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.owner_id: None,
            ResourceBaseDocument.shared_read: [],
            ResourceBaseDocument.shared_write: [],
        }
    )

    # mark the text's index as out-of-date
    await set_index_ood(
        resource_doc.text_id,
        by_public_resource=resource_doc.public,
    )

    # notify users about the new publication
    await notifications.broadcast_user_notification(
        notifications.TemplateIdentifier.USRMSG_RESOURCE_PUBLISHED,
        resource_title=pick_translation(resource_doc.title),
    )

    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpublish",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def unpublish_resource(
    user: SuperuserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    # all fine, unpublish resource
    await resource_doc.set(
        {
            ResourceBaseDocument.public: False,
            ResourceBaseDocument.proposed: False,
        }
    )

    # mark the text's index as out-of-date
    await set_index_ood(
        resource_doc.text_id,
        by_public_resource=True,  # act as if resource public, to force ood status
    )

    return await preprocess_resource_read(resource_doc, user)


@router.get(
    "/{id}/template",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def download_resource_template(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> FileResponse:
    resource_doc = await ResourceBaseDocument.get(
        resource_id,
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise errors.E_403_FORBIDDEN
    text_doc = await TextDocument.get(resource_doc.text_id)

    # import content type for the requested resource
    template = resource_types_mgr.get(
        resource_doc.resource_type
    ).prepare_import_template()
    # apply data from resource instance
    template["resourceId"] = str(resource_doc.id)
    template["_resourceTitle"] = resource_doc.title
    # add resource template README text
    template["__README"] = get_resource_template_readme()

    # construct labels of all locations on the resource's level
    full_location_labels = await text_doc.full_location_labels(resource_doc.level)

    # fill in content templates with IDs and some informational fields
    template["contents"] = [
        dict(
            locationId=str(location.id),
            _position=location.position,
            _location=full_location_labels.get(str(location.id)),
        )
        for location in await LocationDocument.find(
            LocationDocument.text_id == resource_doc.text_id,
            LocationDocument.level == resource_doc.level,
        )
        .sort(+LocationDocument.position)
        .to_list()
    ]

    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")  # noqa: SIM115 (intentional)
    tempfile.write(json.dumps(template, indent=2, sort_keys=True))
    tempfile.flush()

    # prepare headers ... according to
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
    # the filename should be quoted, but then Safari decides to download the file
    # with a quoted filename :(
    headers = {
        "Content-Disposition": (
            f"attachment; filename={text_doc.slug}_{resource_doc.id}_template.json"
        )
    }

    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        path=tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


async def _import_resource_contents_task(
    resource_id: PydanticObjectId,
    file_bytes: bytes,
    user: UserRead,
) -> dict[str, Any]:
    # check if resource exists
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id, with_children=True
    ).exists():
        raise errors.E_404_RESOURCE_NOT_FOUND

    # check if user has permission to write to this resource, if so, fetch from DB
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_403_FORBIDDEN

    # parse data and validate import file format
    try:
        import_data = json.loads(file_bytes)
    except Exception as e:
        raise errors.update_values(
            exc=errors.E_400_UPLOAD_INVALID_JSON,
            values={"errors": str(e)},
        )
    finally:
        del file_bytes

    # check if resource_id matches the one in the import file
    if str(resource_id) != str(import_data.get("resourceId")):
        raise errors.E_400_IMPORT_ID_MISMATCH  # pragma: no cover

    # chek if "contents" is a list
    if not isinstance(import_data.get("contents"), list):
        raise errors.E_422_UPLOAD_INVALID_DATA

    # get content models
    content_model = resource_types_mgr.get(resource_doc.resource_type).content_model()
    doc_model: ContentBaseDocument = content_model.document_model()
    update_model = content_model.update_model()

    created_count = 0
    updated_count = 0
    contents = []  # [(<content_doc: ContentBaseDocument>, <is_update: bool>)]

    try:
        # check import data
        while import_data.get("contents"):
            content = import_data["contents"].pop(0)

            # check if location ID is valid
            if not content.get("locationId") or not PydanticObjectId.is_valid(
                content.get("locationId")
            ):
                raise errors.E_400_IMPORT_ID_NON_EXISTENT
            loc_id = PydanticObjectId(content.get("locationId"))
            # remove location ID from content data
            # to pass update model validation
            del content["locationId"]

            # check if location exists
            if not await LocationDocument.find_one(
                LocationDocument.id == loc_id
            ).exists():
                raise errors.E_400_IMPORT_ID_NON_EXISTENT

            # check if this content already exists
            content_doc = await doc_model.find_one(
                doc_model.resource_id == resource_doc.id,
                doc_model.location_id == loc_id,
            )

            # validate content against model
            try:
                if content_doc:
                    await content_doc.apply_updates(
                        update_model(
                            resource_type=resource_doc.resource_type,
                            **content,
                        ),
                        replace=False,
                    )
                    contents.append((content_doc, True))
                else:
                    content_doc = doc_model(
                        resource_type=resource_doc.resource_type,
                        resource_id=resource_doc.id,
                        location_id=loc_id,
                        **content,
                    )
                    contents.append((content_doc, False))
            except Exception as e:
                print(e)
                raise errors.E_422_UPLOAD_INVALID_DATA

        # write import data
        while contents:
            content_doc, is_update = contents.pop(0)
            if is_update:
                await content_doc.replace()
                updated_count += 1
            else:
                await content_doc.save()
                created_count += 1
    except Exception as e:
        raise e
    finally:
        del import_data, contents
        # call the resource's hook for changed contents
        await resource_doc.contents_changed_hook()
        # mark the text's index as out-of-date
        await set_index_ood(
            resource_doc.text_id,
            by_public_resource=resource_doc.public,
        )

    return {
        "created": created_count,
        "updated": updated_count,
    }


@router.post(
    "/{id}/import",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON,
        ]
    ),
)
async def import_resource_contents(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
    file: Annotated[
        UploadFile,
        File(
            description="JSON file containing the resource content data",
            media_type="application/json",
        ),
    ],
) -> tasks.TaskDocument:
    # test upload file MIME type
    if file.content_type.lower() != "application/json":
        raise errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON

    file_bytes = await file.read()
    await file.close()
    return await tasks.create_task(
        _import_resource_contents_task,
        tasks.TaskType.RESOURCE_IMPORT,
        target_id=resource_id,
        user_id=user.id,
        task_kwargs={
            "resource_id": resource_id,
            "file_bytes": file_bytes,
            "user": user,
        },
    )


async def _export_resource_contents_task(
    user: OptionalUserDep,
    cfg: TekstConfig,
    resource_id: PydanticObjectId,
    export_format: ResourceExportFormat,
    location_from_id: PydanticObjectId | None,
    location_to_id: PydanticObjectId | None,
) -> dict[str, Any]:
    # check if resource exists
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        with_children=True,
    ).exists():
        raise errors.E_404_RESOURCE_NOT_FOUND

    # check if user has permission to read this resource, if so, fetch from DB
    resource: ResourceBaseDocument = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # check if location range is valid
    loc_from: LocationDocument = (
        await LocationDocument.get(location_from_id) if location_from_id else None
    )
    loc_to: LocationDocument = (
        await LocationDocument.get(location_to_id) if location_to_id else None
    )
    if (
        (loc_from and loc_from.text_id != resource.text_id)
        or (loc_to and loc_to.text_id != resource.text_id)
        or (loc_from and loc_from.level != resource.level)
        or (loc_to and loc_to.level != resource.level)
        or (loc_from and loc_to and loc_from.position > loc_to.position)
    ):
        raise errors.E_400_LOCATION_RANGE_INVALID

    text = await TextDocument.get(resource.text_id)
    target_resource_type = resource_types_mgr.get(resource.resource_type)

    # get target location IDs from range
    target_loc_id_pos_map = {
        loc.id: loc.position
        for loc in await LocationDocument.find(
            LocationDocument.text_id == resource.text_id,
            LocationDocument.level == resource.level,
            GTE(LocationDocument.position, loc_from.position) if loc_from else {},
            LTE(LocationDocument.position, loc_to.position) if loc_to else {},
        )
        .sort(+LocationDocument.position)
        .to_list()
    }

    # get target contents
    content_doc_model = target_resource_type.content_model().document_model()
    contents = await content_doc_model.find(
        content_doc_model.resource_id == resource.id,
        In(content_doc_model.location_id, target_loc_id_pos_map.keys()),
        with_children=True,
    ).to_list()

    # sort target contents
    contents.sort(key=lambda c: target_loc_id_pos_map[c.location_id])
    target_loc_id_pos_map = None

    # construct temp file name and path
    tempfile_name = str(uuid4())
    tempfile_path: PathObj = cfg.temp_files_dir / tempfile_name

    # create export data
    if export_format == "tekst-json":
        await target_resource_type.export_tekst_json(
            resource=resource,
            contents=contents,
            file_path=tempfile_path,
        )
    elif export_format == "json":
        await target_resource_type.export_universal_json(
            resource=resource,
            contents=contents,
            file_path=tempfile_path,
        )
    else:
        try:
            await target_resource_type.export(
                resource=resource,
                contents=contents,
                export_format=export_format,
                file_path=tempfile_path,
            )
        except ValueError:
            raise errors.E_400_UNSUPPORTED_EXPORT_FORMAT

    fmt = res_exp_fmt_info[export_format]
    filename = f"{text.slug}_{resource.id}_export.{fmt['extension']}"

    return {
        "filename": filename,
        "artifact": tempfile_name,
        "mimetype": fmt["mimetype"],
    }


@router.get(
    "/{id}/export",
    response_model=tasks.TaskRead,
    status_code=status.HTTP_202_ACCEPTED,
)
async def export_resource_contents(
    user: OptionalUserDep,
    cfg: ConfigDep,
    request: Request,
    resource_id: Annotated[
        PydanticObjectId,
        Path(
            alias="id",
            description="ID of the resource to export",
        ),
    ],
    export_format: Annotated[
        ResourceExportFormat,
        Query(
            alias="format",
            description="Export format",
        ),
    ] = "json",
    location_from_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="from",
            description="ID of the location to start the export's location range from",
        ),
    ] = None,
    location_to_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="to",
            description="ID of the location to end the export's location range at",
        ),
    ] = None,
) -> tasks.TaskDocument:
    return await tasks.create_task(
        _export_resource_contents_task,
        tasks.TaskType.RESOURCE_EXPORT,
        user_id=user.id if user else None,
        target_id=user.id if user else request.client.host,
        task_kwargs={
            "user": user,
            "cfg": cfg,
            "resource_id": resource_id,
            "export_format": export_format,
            "location_from_id": location_from_id,
            "location_to_id": location_to_id,
        },
    )


@router.get(
    "/{id}/aggregations",
    status_code=status.HTTP_200_OK,
    response_model=list[AnnotationAggregation],
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_INVALID_REQUEST_DATA,
        ]
    ),
)
async def get_annotation_aggregations(
    user: OptionalUserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(
            alias="id",
        ),
    ],
) -> list:
    # try to get resource doc to check if access is allowed for user
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    if not resource_doc.resource_type == "textAnnotation":
        raise errors.E_400_INVALID_REQUEST_DATA
    # find requested precomputed data
    precomp_doc = await PrecomputedDataDocument.find_one(
        PrecomputedDataDocument.ref_id == resource_doc.id,
        PrecomputedDataDocument.precomputed_type == "aggregations",
    )
    if precomp_doc and precomp_doc.data:
        return precomp_doc.data
    else:
        return []


@router.get(
    "/{id}/coverage",
    status_code=status.HTTP_200_OK,
    response_model=ResourceCoverage,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_resource_coverage_data(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> dict:
    # try to get resource doc to check if access is allowed for user
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND
    # find requested precomputed data
    precomp_doc = await PrecomputedDataDocument.find_one(
        PrecomputedDataDocument.ref_id == resource_doc.id,
        PrecomputedDataDocument.precomputed_type == "coverage",
    )
    if precomp_doc and precomp_doc.data:
        return precomp_doc.data
    else:
        raise errors.E_404_NOT_FOUND
