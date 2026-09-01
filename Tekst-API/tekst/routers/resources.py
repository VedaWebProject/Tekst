import json

from pathlib import Path as PathObj
from tempfile import NamedTemporaryFile
from typing import Annotated, Any, get_args
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import GTE, LTE, Eq, In
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
from starlette.background import BackgroundTask

from tekst import errors, notifications, tasks
from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.config import ConfigDep, TekstConfig
from tekst.i18n import pick_translation
from tekst.logs import log
from tekst.models.common import DocumentBase
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.correction import CorrectionDocument
from tekst.models.location import LocationDocument
from tekst.models.notifications import Notification
from tekst.models.precomputed import PrecomputedDataDocument
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceCoverage,
    ResourceExportFormat,
    res_exp_fmt_info,
)
from tekst.models.resource_unions import (
    AnyResourceCreate,
    AnyResourceRead,
    AnyResourceUpdate,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.notifications import send_notification
from tekst.resources import (
    RES_EXCLUDE_EXP_IMP,
    call_resource_precompute_hooks,
    resource_types_mgr,
)
from tekst.state import StateDep
from tekst.types import ResourceTypeName
from tekst.utils import client_hash, ensure


async def prepare_resource_read(
    resource_doc: ResourceBaseDocument,
    for_user: UserRead | None = None,
) -> AnyResourceRead:
    """
    A helper function that returns a fully prepared resource read instance for clients,
    masked according to the requesting user's permissions.
    """
    # convert resource document to resource type's read model instance
    resource: AnyResourceRead = (
        resource_types_mgr.get(resource_doc.resource_type)
        .resource_model()
        .read_model()(
            **resource_doc.model_dump(exclude=resource_doc.restricted_fields(for_user))
        )
    )
    assert isinstance(resource, get_args(AnyResourceRead)[0])  # for type checker

    # include writable flag
    resource.writable = bool(
        for_user
        and (
            for_user.is_superuser
            or (
                (
                    for_user.id in resource.owner_ids
                    or for_user.id in resource_doc.shared_write
                )
                and not resource.proposed
            )
        )
    )

    # include owner(s) user data in each resource model (if owner IDs are set)
    if resource.owner_ids:
        resource.owners = [
            UserReadPublic.model_from(owner)
            for owner in await UserDocument.find(
                In(UserDocument.id, resource.owner_ids)
            ).to_list()
        ]

    # include corrections count if user is owner of the resource
    # or, if resource has no owner(s), user is superuser
    if for_user and (
        for_user.is_superuser
        or for_user.id in resource.owner_ids
        or for_user.id in resource.shared_write
    ):
        resource.corrections = await CorrectionDocument.find(
            CorrectionDocument.resource_id == resource.id
        ).count()

    # include shared-with user data in each resource model (if any)
    if for_user and (for_user.is_superuser or for_user.id in resource.owner_ids):
        if resource.shared_read:
            resource.shared_read_users = [
                UserReadPublic.model_from(u)
                for u in await UserDocument.find(
                    In(UserDocument.id, resource.shared_read)
                ).to_list()
            ]
        if resource.shared_write:
            resource.shared_write_users = [
                UserReadPublic.model_from(u)
                for u in await UserDocument.find(
                    In(UserDocument.id, resource.shared_write)
                ).to_list()
            ]
    else:
        resource.shared_read = []
        resource.shared_write = []

    return resource


router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)


@router.get(
    "/precompute",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def trigger_cache_precomputation(
    su: SuperuserDep,
    force: bool = False,
) -> tasks.TaskDocument:
    return await tasks.create_task(
        call_resource_precompute_hooks,
        tasks.TaskType.PRECOMPUTE_DATA,
        user_id=su.id,
        task_kwargs={"force": force},
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
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_resource(
    resource: AnyResourceCreate,
    user: UserDep,
    cfg: ConfigDep,
    state: StateDep,
) -> AnyResourceRead:
    # check user resources limit
    if (
        not user.is_superuser
        and await ResourceBaseDocument.user_resource_count(user.id)
        >= cfg.misc.max_resources_per_user
    ):
        raise errors.E_409_RESOURCES_LIMIT_REACHED

    # check if creation of this resource type is allowed for user
    if not user.is_superuser and resource.resource_type in state.deny_resource_types:
        raise errors.E_403_FORBIDDEN

    # check text integrity
    text = await TextDocument.get(resource.text_id)
    if not text:
        raise errors.E_400_INVALID_TEXT
    if resource.level > len(text.levels) - 1:
        raise errors.E_400_RESOURCE_INVALID_LEVEL

    # find document model for this resource type, instantiate, create
    resource_doc: ResourceBaseDocument = (
        resource_types_mgr.get(resource.resource_type)
        .resource_model()
        .document_model()
        .model_from(resource)
    )
    resource_doc.owner_ids = [user.id]  # force correct owner ID
    await resource_doc.create()  # create resource in DB

    return await prepare_resource_read(resource_doc, user)


@router.post(
    "/{id}/patch",
    response_model=AnyResourceRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_RESOURCE_PATCH_OF_PATCH,
        ]
    ),
)
async def create_resource_patch(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)

    # check if resource is already a patch
    if resource_doc.patch_for:
        raise errors.E_400_RESOURCE_PATCH_OF_PATCH

    # generate patch title
    patch_title_suffix = " v" + str(
        await ResourceBaseDocument.find(
            ResourceBaseDocument.patch_for == resource_id,
            with_children=True,
        ).count()
        + 2
    )
    patch_title = [
        {
            "locale": tt.get("locale", "*"),
            "translation": tt.get("translation", "")[0 : 64 - len(patch_title_suffix)]
            + patch_title_suffix,
        }
        for tt in resource_doc.title
    ]

    # create modified copy of resource doc
    patch_doc: ResourceBaseDocument = await resource_doc.model_copy(
        update={
            "id": None,
            "title": patch_title,
            "patch_for": resource_doc.id,
            "owner_ids": [user.id],
            "proposed": False,
            "public": False,
            "shared_read": [],
            "shared_write": [],
        }
    ).create()

    return await prepare_resource_read(patch_doc, user)


@router.patch(
    "/{id}",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def update_resource(
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
    updates: AnyResourceUpdate,
    user: UserDep,
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(
        resource_id,
        user,
        write_access=True,
    )

    # prevent shares modification by non-owners and non-superusers,
    # generally prevent shares modification for proposed and public resources
    if (
        (not user.is_superuser and user.id not in resource_doc.owner_ids)
        or resource_doc.proposed
        or resource_doc.public
    ):
        updates.shared_read = resource_doc.shared_read
        updates.shared_write = resource_doc.shared_write
    # else, validate shares combination
    else:
        # make sure shares are set on updates
        # so we can further validate them in one place
        updates.shared_read = (
            updates.shared_read
            if updates.shared_read is not None
            else resource_doc.shared_read
        )
        updates.shared_write = (
            updates.shared_write
            if updates.shared_write is not None
            else resource_doc.shared_write
        )
        # exclude write shares from read shares as they are implicit
        updates.shared_read = [
            user_id
            for user_id in updates.shared_read
            if user_id not in updates.shared_write
        ]
        # remove invalid user IDs from shares
        updates.shared_read = [
            uid
            for uid in updates.shared_read
            if await UserDocument.find_one(UserDocument.id == uid).exists()
        ]
        updates.shared_write = [
            uid
            for uid in updates.shared_write
            if await UserDocument.find_one(UserDocument.id == uid).exists()
        ]

    # mark respective text's index as out-of-date if any indexing-relevant config
    # will be changed by this update
    if resource_doc.cfg_updates_invalidate_index(updates):
        await resource_doc.set_index_ood()

    # update document
    await resource_doc.apply_updates(updates)

    return await prepare_resource_read(resource_doc, user)


@router.get(
    "",
    response_model=list[AnyResourceRead],
    status_code=status.HTTP_200_OK,
)
async def find_resources(
    user: OptionalUserDep,
    text_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="txt",
            description="ID of text to find resources for",
        ),
    ] = None,
    level: Annotated[
        int | None,
        Query(
            alias="lvl",
            description="Structure level to find resources for",
        ),
    ] = None,
    resource_type: Annotated[
        ResourceTypeName | None,
        Query(
            alias="type",
            description="Type of resources to find",
        ),
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
            await ResourceBaseDocument.query_criteria_read(user),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    # return processed results, enrich with user-specific access flags etc.
    return [
        await prepare_resource_read(resource_doc, user)
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
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    return await prepare_resource_read(resource_doc, user)


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
        Path(alias="id"),
    ],
) -> None:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if not user.is_superuser and user.id not in resource_doc.owner_ids:
        raise errors.E_403_FORBIDDEN  # pragma: no cover
    if resource_doc.public:
        raise errors.E_400_RESOURCE_PUBLIC_DELETE
    if resource_doc.proposed:
        raise errors.E_400_RESOURCE_PROPOSED_DELETE

    # all fine
    # turn patches of this resource into original resources
    await ResourceBaseDocument.find(
        ResourceBaseDocument.patch_for == resource_id,
        with_children=True,
    ).set({ResourceBaseDocument.patch_for: None})

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
    await resource_doc.set_index_ood()

    # delete resource itself
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        with_children=True,
    ).delete()


@router.patch(
    "/{id}/owners",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
            errors.E_403_RESOURCE_PUBLIC_INVALID_OWNER,
            errors.E_400_TARGET_USER_NON_EXISTENT,
        ]
    ),
)
async def update_resource_owners(
    user: UserDep,
    cfg: ConfigDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    owner_ids: Annotated[list[PydanticObjectId], Body(min_length=1)],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    # check if requesting user is allowed to change owners
    if not user.is_superuser and user.id not in resource_doc.owner_ids:
        raise errors.E_403_FORBIDDEN  # pragma: no cover
    if not user.is_superuser and (resource_doc.public or resource_doc.proposed):
        raise errors.E_403_FORBIDDEN

    # check if target users exist
    for new_owner_id in owner_ids:
        owner = await UserDocument.get(new_owner_id)
        if not owner:
            raise errors.E_400_TARGET_USER_NON_EXISTENT

    # remember old owner_ids
    old_owner_ids = [uid for uid in resource_doc.owner_ids]

    # all fine, set owners and remove target user IDs from resource shares
    await resource_doc.set(
        {
            ResourceBaseDocument.owner_ids: owner_ids,
            ResourceBaseDocument.shared_read: [
                uid for uid in resource_doc.shared_read if uid not in owner_ids
            ],
            ResourceBaseDocument.shared_write: [
                uid for uid in resource_doc.shared_write if uid not in owner_ids
            ],
        }
    )

    # notify newly added owners
    for u in await UserDocument.find(
        In(UserDocument.id, list(set(owner_ids) - set(old_owner_ids))),
        Eq(
            UserDocument.user_notification_triggers,
            Notification.EMAIL_ADDED_AS_OWNER.value,
        ),
    ).to_list():
        await send_notification(
            u,
            Notification.EMAIL_ADDED_AS_OWNER,
            username=user.username,
            resource_title=pick_translation(
                resource_doc.title,
                u.locale or "enUS",
            ),
        )

    # notify removed owners
    for u in await UserDocument.find(
        In(UserDocument.id, list(set(old_owner_ids) - set(owner_ids))),
        Eq(
            UserDocument.user_notification_triggers,
            Notification.EMAIL_REMOVED_FROM_OWNERS.value,
        ),
    ).to_list():
        await send_notification(
            u,
            Notification.EMAIL_REMOVED_FROM_OWNERS,
            username=user.username,
            resource_title=pick_translation(
                resource_doc.title,
                u.locale or "enUS",
            ),
        )

    return await prepare_resource_read(resource_doc, user)


@router.post(
    "/{id}/propose",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_403_FORBIDDEN,
            errors.E_400_RESOURCE_PATCH_PROPOSE,
        ]
    ),
)
async def propose_resource(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if not user.is_superuser and user.id not in resource_doc.owner_ids:
        raise errors.E_403_FORBIDDEN  # pragma: no cover
    if resource_doc.proposed:
        return await prepare_resource_read(resource_doc, user)
    if resource_doc.public:
        raise errors.E_400_RESOURCE_PROPOSE_PUBLIC
    if resource_doc.patch_for:
        raise errors.E_400_RESOURCE_PATCH_PROPOSE
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
        notifications.Notification.USRMSG_RESOURCE_PROPOSED,
        username=user.name if "name" in user.public_fields else user.username,
        resource_title=pick_translation(resource_doc.title),
    )
    return await prepare_resource_read(resource_doc, user)


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
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if not user.is_superuser and user.id not in resource_doc.owner_ids:
        raise errors.E_403_FORBIDDEN
    # all fine, unpropose resource
    await resource_doc.set(
        {
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.public: False,
            ResourceBaseDocument.supporters: None,
        }
    )
    return await prepare_resource_read(resource_doc, user)


@router.post(
    "/{id}/support",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_INVALID_REQUEST_DATA,
        ]
    ),
)
async def support_resource(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if not resource_doc.proposed or user.id in resource_doc.owner_ids:
        raise errors.E_400_INVALID_REQUEST_DATA
    if resource_doc.supporters is not None and user.id in resource_doc.supporters:
        return await prepare_resource_read(resource_doc, user)
    await resource_doc.set(
        {
            ResourceBaseDocument.supporters: list(
                set((resource_doc.supporters or []) + [user.id])
            ),
        }
    )
    return await prepare_resource_read(resource_doc, user)


@router.post(
    "/{id}/unsupport",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_INVALID_REQUEST_DATA,
        ]
    ),
)
async def unsupport_resource(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if (
        not resource_doc.proposed
        or user.id in resource_doc.owner_ids
        or resource_doc.supporters is None
        or user.id not in resource_doc.supporters
    ):
        raise errors.E_400_INVALID_REQUEST_DATA
    await resource_doc.set(
        {
            ResourceBaseDocument.supporters: [
                s_id for s_id in resource_doc.supporters if s_id != user.id
            ],
        }
    )
    return await prepare_resource_read(resource_doc, user)


@router.post(
    "/{id}/publish",
    response_model=AnyResourceRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_400_RESOURCE_PUBLISH_UNPROPOSED,
            errors.E_400_RESOUCE_PATCH_PUBLISH,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def publish_resource(
    user: SuperuserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    if resource_doc.public:
        return await prepare_resource_read(resource_doc, user)
    if not resource_doc.proposed:
        raise errors.E_400_RESOURCE_PUBLISH_UNPROPOSED
    if resource_doc.patch_for:
        raise errors.E_400_RESOUCE_PATCH_PUBLISH

    # all fine, publish resource
    await resource_doc.set(
        {
            ResourceBaseDocument.public: True,
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.supporters: None,
            ResourceBaseDocument.owner_ids: [user.id],
            ResourceBaseDocument.shared_read: [],
            ResourceBaseDocument.shared_write: [],
        }
    )

    # mark the text's index as out-of-date
    await resource_doc.set_index_ood()

    # notify users about the new publication
    await notifications.broadcast_user_notification(
        notifications.Notification.USRMSG_RESOURCE_PUBLISHED,
        resource_title=pick_translation(resource_doc.title),
    )

    return await prepare_resource_read(resource_doc, user)


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
    user: SuperuserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    await resource_doc.set(
        {
            ResourceBaseDocument.public: False,
            ResourceBaseDocument.proposed: False,
        }
    )
    await resource_doc.set_index_ood()
    return await prepare_resource_read(resource_doc, user)


@router.get(
    "/{id}/template",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def download_resource_template(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> FileResponse:
    resource_doc = await ResourceBaseDocument.get_safe(
        resource_id,
        user,
        write_access=True,
    )
    text = ensure(await TextDocument.get(resource_doc.text_id))

    # import content type for the requested resource
    readme = resource_types_mgr.get(
        resource_doc.resource_type
    ).get_res_import_readme_obj()
    # apply data from resource instance
    readme["_resourceTitle"] = pick_translation(
        resource_doc.title,
        user.locale or "enUS",
    )

    # construct labels of all locations on the resource's level
    full_loc_labels = await text.full_location_labels(resource_doc.level)

    # fill in content templates with IDs and some informational fields
    content_templates = [
        dict(
            locationId=str(location.id),
            _position=location.position,
            _location=full_loc_labels.get(str(location.id)),
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
    tempfile.write(json.dumps(readme, indent=None, sort_keys=True) + "\n")
    tempfile.writelines([json.dumps(t, indent=None) + "\n" for t in content_templates])
    tempfile.flush()

    # prepare headers ... according to
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
    # the filename should be quoted, but then Safari decides to download the file
    # with a quoted filename :(
    headers = {
        "Content-Disposition": (
            f"attachment; filename={text.slug}_{resource_doc.id}_template.jsonl"
        )
    }

    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        path=tempfile.name,
        headers=headers,
        media_type="application/json-lines",
        background=BackgroundTask(tempfile.close),
    )


async def _import_resource_task(
    resource_id: PydanticObjectId,
    file_bytes: bytes,
    user: UserRead,
) -> dict[str, Any]:
    # check if user has permission to write to this resource, if so, fetch from DB
    resource_doc = await ResourceBaseDocument.find_one(
        Eq(ResourceBaseDocument.id, resource_id),
        await ResourceBaseDocument.query_criteria_write(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    # get content models
    content_model = resource_types_mgr.get(resource_doc.resource_type).content_model()
    content_doc_model: type[ContentBase] = content_model.document_model()
    assert issubclass(content_doc_model, DocumentBase)  # for type checker
    content_create_model: type[ContentBase] = content_model.create_model()

    if not file_bytes.decode("utf-8").strip():
        return {
            "created": 0,
            "updated": 0,
        }

    lines = file_bytes.strip().split(b"\n")
    res_updates: AnyResourceUpdate | None = None

    ### prepare input data

    try:
        # remove possible README object from first line
        first_obj = json.loads(lines[0].decode("utf-8"))
        if "__README" in first_obj:
            lines.pop(0)
        # get possible resource metadata from first (/second) line
        first_obj = json.loads(lines[0].decode("utf-8"))
    except Exception as e:
        raise errors.update_values(
            exc=errors.E_400_INVALID_REQUEST_DATA,
            values={"errors": str(e)},
        )
    # normalize resource ID key to allow following the import template as well as
    # re-importing a Tekst-JSONL-exported resource
    first_obj["_id"] = first_obj.pop("id", first_obj.pop("_id", None))
    # if it really seems to be resource metadata, validate it
    if first_obj.get("_id"):
        if first_obj["_id"] == str(resource_id):
            first_obj["resource_type"] = resource_doc.resource_type
            res_updates = (
                resource_types_mgr.get(resource_doc.resource_type)
                .resource_model()
                .update_model()(
                    **{
                        k: v
                        for k, v in first_obj.items()
                        if k not in RES_EXCLUDE_EXP_IMP
                    },
                    resource_type=resource_doc.resource_type,
                )
            )
        else:  # pragma: no cover
            raise errors.E_400_INVALID_REQUEST_DATA
        lines.pop(0)

    ### validate contents
    ### (without doing anything with them yet, we just want to
    ### fail early on errors before writing anything to the DB)

    contents_data = []
    for line in lines:
        if not line.strip():  # pragma: no cover
            continue

        # decode and parse line
        try:
            c_obj = json.loads(line.decode("utf-8"))
        except Exception as e:  # pragma: no cover
            raise errors.update_values(
                exc=errors.E_400_UPLOAD_INVALID_JSON,
                values={"errors": str(e)},
            )

        # handle content
        # check if location ID is valid
        if not c_obj.get("locationId") or not PydanticObjectId.is_valid(
            c_obj["locationId"]
        ):
            raise errors.E_400_IMPORT_ID_NON_EXISTENT
        loc_id = PydanticObjectId(c_obj["locationId"])

        # check if location exists
        if not await LocationDocument.find_one(LocationDocument.id == loc_id).exists():
            raise errors.E_400_IMPORT_ID_NON_EXISTENT

        # validate agains content data models
        try:
            # validate against create model
            content_create_model(
                resource_id=resource_doc.id,
                resource_type=resource_doc.resource_type,
                **c_obj,
            )
            contents_data.append(c_obj)
        except Exception as e:
            raise errors.update_values(
                exc=errors.E_422_UPLOAD_INVALID_DATA,
                values={"errors": str(e)},
            )

    del lines

    ### process content updates

    updates_count = 0
    inserts_count = 0
    todo_stack = []

    while contents_data:
        content_import_doc = content_doc_model(
            resource_id=resource_id,
            resource_type=resource_doc.resource_type,
            **contents_data.pop(),
        )
        existing_content_doc = await ContentBaseDocument.find_one(
            Eq(ContentBaseDocument.resource_id, resource_doc.id),
            Eq(ContentBaseDocument.location_id, content_import_doc.location_id),
            Eq(ContentBaseDocument.archived, False),
            with_children=True,
        )

        # handle existing content deletion / archival
        if existing_content_doc:
            updates_count += 1
            if resource_doc.public and not resource_doc.patch_for:
                # archive the existing content doc if the resource
                # is public (and not a resource patch)
                await existing_content_doc.archive()
            else:
                # otherwise, delete it
                await existing_content_doc.delete()  # pragma: no cover
        else:
            inserts_count += 1

        todo_stack.append(content_import_doc)
        if len(todo_stack) > 100:  # pragma: no cover
            await content_doc_model.insert_many(todo_stack)
            todo_stack = []

    if len(todo_stack):
        await content_doc_model.insert_many(todo_stack)

    del contents_data
    del todo_stack

    # write resource props and config import data
    # (skipped if anything went wrong with content import)
    await resource_doc.apply_updates(res_updates)
    # call the resource's hook for changed contents
    await resource_doc.contents_changed_hook()
    # mark the text's index as out-of-date
    await resource_doc.set_index_ood()

    return {
        "created": inserts_count,
        "updated": updates_count,
    }


@router.post(
    "/{id}/import",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
)
async def import_resource(
    user: UserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
    file: Annotated[
        UploadFile,
        File(
            description="JSONL (JSON lines) file containing the resource data",
            media_type="application/json-lines",
        ),
    ],
) -> tasks.TaskDocument:
    file_bytes = await file.read()
    await file.close()
    return await tasks.create_task(
        _import_resource_task,
        tasks.TaskType.RESOURCE_IMPORT,
        target_id=resource_id,
        user_id=user.id,
        task_kwargs={
            "resource_id": resource_id,
            "file_bytes": file_bytes,
            "user": user,
        },
    )


async def export_resource_contents_task(
    user: OptionalUserDep,
    cfg: TekstConfig,
    resource_id: PydanticObjectId,
    export_format: ResourceExportFormat,
    location_from_id: PydanticObjectId | None = None,
    location_to_id: PydanticObjectId | None = None,
) -> dict[str, Any]:
    resource = await ResourceBaseDocument.get_safe(resource_id, user)
    # check if location range is valid
    loc_from: LocationDocument | None = (
        await LocationDocument.get(location_from_id) if location_from_id else None
    )
    loc_to: LocationDocument | None = (
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

    text = ensure(await TextDocument.get(resource.text_id))
    target_res_type = resource_types_mgr.get(resource.resource_type)

    # get the IDs of all resource contents in the given location range,
    # sorted by the position of their reference location
    content_ids = (
        await LocationDocument.find(
            Eq(LocationDocument.text_id, resource.text_id),
            Eq(LocationDocument.level, resource.level),
            # query for location range
            GTE(LocationDocument.position, loc_from.position) if loc_from else {},
            LTE(LocationDocument.position, loc_to.position) if loc_to else {},
        )
        .aggregate(
            [
                # find contents for these locations
                {
                    "$lookup": {
                        "from": "contents",
                        "localField": "_id",
                        "foreignField": "location_id",
                        "let": {
                            "location_id": "$_id",
                            "resource_id": resource_id,
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$location_id", "$$location_id"]},
                                            {"$eq": ["$resource_id", "$$resource_id"]},
                                            {"$eq": ["$archived", False]},
                                        ]
                                    }
                                }
                            },
                            {"$project": {"_id": 1}},
                        ],
                        "as": "contents",
                    }
                },
                # drop locations without contents
                {"$match": {"$expr": {"$gt": [{"$size": "$contents"}, 0]}}},
                # sort locations by position
                {"$sort": {"position": 1}},
                # only keep content IDs
                {"$project": {"_id": {"$arrayElemAt": ["$contents._id", 0]}}},
            ]
        )
        .to_list()
    )
    content_ids: list[PydanticObjectId] = [c["_id"] for c in content_ids]

    # construct temp file name and path
    tempfile_name = str(uuid4())
    tempfile_path: PathObj = cfg.temp_files_dir / tempfile_name

    # create export data
    if export_format == "tekst-jsonl":
        await target_res_type.export_tekst_jsonl(
            resource=resource,
            content_ids=content_ids,
            file_path=tempfile_path,
        )
    elif export_format == "json":
        await target_res_type.export_universal_json(
            resource=resource,
            content_ids=content_ids,
            file_path=tempfile_path,
        )
    else:
        try:
            await target_res_type.export(
                resource=resource,
                content_ids=content_ids,
                export_format=export_format,
                file_path=tempfile_path,
            )
        except ValueError:  # pragma: no cover
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
    responses=errors.responses(
        [
            errors.E_403_FORBIDDEN,
        ]
    ),
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
    # allow export format "tekst-jsonl" only for logged-in users
    if not user and export_format == "tekst-jsonl":
        raise errors.E_403_FORBIDDEN
    # create and return background task
    return await tasks.create_task(
        export_resource_contents_task,
        tasks.TaskType.RESOURCE_EXPORT,
        user_id=user.id if user else None,
        target_id=user.id
        if user
        else client_hash(request, behind_reverse_proxy=cfg.behind_reverse_proxy),
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
    response_model=list[Any],
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_aggregations(
    user: OptionalUserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
) -> list[Any]:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
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
            errors.E_404_NOT_FOUND,
        ]
    ),
)
async def get_resource_coverage_data(
    resource_id: Annotated[
        PydanticObjectId,
        Path(alias="id"),
    ],
    user: OptionalUserDep,
) -> dict:
    resource_doc = await ResourceBaseDocument.get_safe(resource_id, user)
    # find requested precomputed data
    precomp_doc = await PrecomputedDataDocument.find_one(
        PrecomputedDataDocument.ref_id == resource_doc.id,
        PrecomputedDataDocument.precomputed_type == "coverage",
    )
    if precomp_doc and precomp_doc.data:
        return precomp_doc.data
    else:
        raise errors.E_404_NOT_FOUND
