import json

from tempfile import NamedTemporaryFile
from typing import Annotated

from beanie import PydanticObjectId
from beanie.exceptions import DocumentNotFound
from beanie.operators import In
from bson.errors import InvalidId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    File,
    Path,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import StringConstraints
from starlette.background import BackgroundTask

from tekst import errors, notifications
from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.config import ConfigDep
from tekst.logging import log
from tekst.models.content import ContentBaseDocument
from tekst.models.exchange import ResourceDataImportResponse, ResourceImportData
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.resources import (
    AnyResourceCreateBody,
    AnyResourceRead,
    AnyResourceReadBody,
    AnyResourceUpdateBody,
    get_resource_template_readme,
    resource_types_mgr,
)
from tekst.utils.html import sanitize_dict_html


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
    return resource


router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)


@router.post(
    "",
    response_model=AnyResourceReadBody,
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
    resource: AnyResourceCreateBody, user: UserDep, cfg: ConfigDep
) -> AnyResourceRead:
    # check user resources limit
    if (
        not user.is_superuser
        and await ResourceBaseDocument.user_resource_count(user.id)
        >= cfg.limits_max_resources_per_user
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
    response_model=AnyResourceReadBody,
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
        >= cfg.limits_max_resources_per_user
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
    version_title = (
        resource_doc.title[0 : 64 - len(version_title_suffix)] + version_title_suffix
    )

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
    response_model=AnyResourceReadBody,
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
    updates: AnyResourceUpdateBody,
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
        for user_id in updates.shared_read + updates.shared_write:
            if not await UserDocument.find_one(UserDocument.id == user_id).exists():
                raise errors.E_400_SHARED_WITH_USER_NON_EXISTENT
    # update document with reduced updates
    await resource_doc.apply_updates(
        updates,
        exclude={
            "public",
            "proposed",
            "text_id",
            "owner_id",
            "level",
            "resource_type",
        },
    )
    return await preprocess_resource_read(resource_doc, user)


@router.get(
    "",
    response_model=list[AnyResourceReadBody],
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
    response_model=AnyResourceReadBody,
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
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
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
    # delete resource itself
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        with_children=True,
    ).delete()


@router.post(
    "/{id}/transfer",
    response_model=AnyResourceReadBody,
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
        >= cfg.limits_max_resources_per_user
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
    response_model=AnyResourceReadBody,
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
        resource_title=resource_doc.title,
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpropose",
    response_model=AnyResourceReadBody,
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
    response_model=AnyResourceReadBody,
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
    # notify users about the new publication
    await notifications.broadcast_user_notification(
        notifications.TemplateIdentifier.USRMSG_RESOURCE_PUBLISHED,
        resource_title=resource_doc.title,
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpublish",
    response_model=AnyResourceReadBody,
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
async def get_resource_template(
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
    location_locations = await LocationDocument.get_location_locations(
        text_id=text_doc.id,
        for_level=resource_doc.level,
        loc_delim=text_doc.loc_delim,
    )

    # fill in content templates with IDs and some informational fields
    template["contents"] = [
        dict(
            locationId=str(location.id),
            _position=location.position,
            _location=location_locations.get(str(location.id)),
        )
        for location in await LocationDocument.find(
            LocationDocument.text_id == resource_doc.text_id,
            LocationDocument.level == resource_doc.level,
        )
        .sort(+LocationDocument.position)
        .to_list()
    ]

    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")
    tempfile.write(json.dumps(template, indent=2, sort_keys=True))
    tempfile.flush()

    # prepare headers
    filename = f"{text_doc.slug}_resource_{resource_doc.id}" "_template.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        path=tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


@router.post(
    "/{id}/import",
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON,
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
            errors.E_400_UPLOAD_INVALID_JSON,
            errors.E_400_IMPORT_ID_MISMATCH,
            errors.E_400_IMPORT_ID_NON_EXISTENT,
            errors.E_400_IMPORT_INVALID_CONTENT_DATA,
        ]
    ),
)
async def import_resource_data(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    file: Annotated[
        UploadFile, File(description="JSON file containing the resource data")
    ],
    background_tasks: BackgroundTasks,
) -> ResourceDataImportResponse:
    # test upload file MIME type
    if not file.content_type.lower() == "application/json":
        raise errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON

    # check if resource exists
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id, with_children=True
    ).exists():
        raise errors.E_404_RESOURCE_NOT_FOUND

    # check if user has permission to write to this resource, if so, fetch from DB
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # validate import file format
    try:
        import_data = ResourceImportData.model_validate_json(await file.read())
    except ValueError:
        raise errors.E_400_UPLOAD_INVALID_JSON

    # check if resource_id matches the one in the import file
    if str(resource_id) != str(import_data.resource_id):
        raise errors.E_400_IMPORT_ID_MISMATCH  # pragma: no cover

    # find contents that already exist and have to be updated instead of created
    try:
        existing_contents_dict = {
            str(content_doc.location_id): content_doc
            for content_doc in await ContentBaseDocument.find(
                ContentBaseDocument.resource_id == resource.id,
                In(
                    ContentBaseDocument.location_id,
                    [
                        PydanticObjectId(content_data.get("locationId", ""))
                        for content_data in import_data.contents
                    ],
                ),
                with_children=True,
            ).to_list()
        }
    except InvalidId:  # pragma: no cover
        raise errors.E_400_IMPORT_ID_NON_EXISTENT

    # create lists of validated content updates/creates depending on whether they exist
    contents = {
        "updates": [],
        "creates": [],
    }
    update_model = (
        resource_types_mgr.get(resource.resource_type).content_model().update_model()
    )
    create_model = (
        resource_types_mgr.get(resource.resource_type).content_model().create_model()
    )
    for content_data in import_data.contents:
        is_update = str(content_data.get("locationId", "")) in existing_contents_dict
        contents["updates" if is_update else "creates"].append(
            (update_model if is_update else create_model)(
                resource_id=resource.id,
                resource_type=resource.resource_type,
                **content_data,
            )
        )

    # a sacrifice for the GC
    import_data = None

    # process updates to existing contents
    updated_count = 0
    errors_count = 0
    for update in contents["updates"]:
        update = sanitize_dict_html(update)
        content_doc = existing_contents_dict.get(str(update.location_id))
        if content_doc:
            try:
                await content_doc.apply_updates(
                    update,
                    exclude={"id", "resource_id", "location_id", "resource_type"},
                )
                updated_count += 1
            except (ValueError, DocumentNotFound) as e:  # pragma: no cover
                log.error(e)
                raise errors.E_500_INTERNAL_SERVER_ERROR
                errors_count += 1
        else:  # pragma: no cover
            errors_count += 1

    # process new contents
    content_document_model = (
        resource_types_mgr.get(resource.resource_type).content_model().document_model()
    )
    # get location IDs from target level to check if the ones in new contents are valid
    existing_location_ids = {
        n.id
        for n in await LocationDocument.find(
            LocationDocument.text_id == resource.text_id,
            LocationDocument.level == resource.level,
        ).to_list()
    }
    # filter out contents that reference non-existent location IDs
    contents_creates_len_before = len(contents["creates"])
    contents["creates"] = [
        u for u in contents["creates"] if u.location_id in existing_location_ids
    ]
    errors_count += contents_creates_len_before - len(contents["creates"])
    # sanitize content HTML if any
    contents["creates"] = sanitize_dict_html(contents["creates"])

    # insert new contents
    if len(contents["creates"]):
        insert_many_result = await ContentBaseDocument.insert_many(
            [content_document_model.model_from(c) for c in contents["creates"]],
            ordered=False,
        )
        created_count = len(insert_many_result.inserted_ids)
        errors_count += len(contents["creates"]) - created_count
    else:
        created_count = 0

    # create background task that calls the
    # content's resource's hook for updated content
    background_tasks.add_task(
        resource_types_mgr.get(resource.resource_type).contents_changed_hook,
        resource_id,
    )

    return ResourceDataImportResponse(
        updated=updated_count, created=created_count, errors=errors_count
    )
