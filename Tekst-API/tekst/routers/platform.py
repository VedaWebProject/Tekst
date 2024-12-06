from operator import itemgetter
from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import GTE, LT, NotIn, Or
from fastapi import APIRouter, Header, Path, Query, status
from fastapi.responses import FileResponse
from humps import camelize
from starlette.background import BackgroundTask

from tekst import errors, tasks
from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.config import ConfigDep
from tekst.models.location import LocationDocument
from tekst.models.platform import (
    PlatformData,
    PlatformSecurityInfo,
    PlatformStateDocument,
    PlatformStateRead,
    PlatformStateUpdate,
    PlatformStats,
    TextStats,
)
from tekst.models.resource import ResourceBaseDocument
from tekst.models.segment import (
    ClientSegmentCreate,
    ClientSegmentDocument,
    ClientSegmentHead,
    ClientSegmentRead,
    ClientSegmentUpdate,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.resources import resource_types_mgr
from tekst.routers.texts import get_all_texts
from tekst.state import get_state, update_state


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=PlatformData,
    summary="Get platform data",
    status_code=status.HTTP_200_OK,
)
async def get_platform_data(ou: OptionalUserDep, cfg: ConfigDep) -> dict:
    """Returns data the client needs to initialize"""
    return PlatformData(
        texts=await get_all_texts(ou),
        state=await get_state(),
        security=PlatformSecurityInfo(),
        # find segments with keys starting with "system"
        system_segments=await ClientSegmentDocument.find(
            GTE(ClientSegmentDocument.key, "system"),
            LT(ClientSegmentDocument.key, "systen"),
        ).to_list(),
        # find segments with keys not starting with "system"
        info_segments=await ClientSegmentDocument.find(
            Or(
                LT(ClientSegmentDocument.key, "system"),
                GTE(ClientSegmentDocument.key, "systen"),
            )
        )
        .project(ClientSegmentHead)
        .to_list(),
        tekst=camelize(cfg.tekst),
        max_field_mappings=cfg.es.max_field_mappings,
    )


@router.patch(
    "/settings",
    response_model=PlatformStateRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_platform_settings(
    su: SuperuserDep,
    updates: PlatformStateUpdate,
) -> PlatformStateDocument:
    # reset user locales if the update reduces available locales
    if updates.available_locales and isinstance(updates.available_locales, list):
        await UserDocument.find(
            NotIn(UserDocument.locale, updates.available_locales + [None])
        ).set(
            {
                UserDocument.locale: "enUS"
                if "enUS" in updates.available_locales
                else updates.available_locales[0]
            }
        )
    # apply updates
    return await update_state(**updates.model_dump(exclude_unset=True))


@router.get(
    "/segments/{id}",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
        ]
    ),
)
async def get_segment(
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> ClientSegmentDocument:
    segment = await ClientSegmentDocument.get(segment_id)
    if not segment:
        raise errors.E_404_SEGMENT_NOT_FOUND
    return segment


@router.post(
    "/segments",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_SEGMENT_KEY_LOCALE_CONFLICT,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_segment(
    su: SuperuserDep,
    segment: ClientSegmentCreate,
) -> ClientSegmentDocument:
    if await ClientSegmentDocument.find_one(
        ClientSegmentDocument.key == segment.key,
        ClientSegmentDocument.locale == segment.locale,
    ).exists():
        raise errors.E_409_SEGMENT_KEY_LOCALE_CONFLICT
    return await ClientSegmentDocument.model_from(segment).create()


@router.patch(
    "/segments/{id}",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: ClientSegmentUpdate,
) -> ClientSegmentDocument:
    segment_doc = await ClientSegmentDocument.get(segment_id)
    if not segment_doc:
        raise errors.E_404_SEGMENT_NOT_FOUND
    return await segment_doc.apply_updates(updates)


@router.delete(
    "/segments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    if not await ClientSegmentDocument.find_one(
        ClientSegmentDocument.id == segment_id
    ).exists():
        raise errors.E_404_SEGMENT_NOT_FOUND
    delete_result = await ClientSegmentDocument.find_one(
        ClientSegmentDocument.id == segment_id
    ).delete()
    if (
        not delete_result.acknowledged or not delete_result.deleted_count
    ):  # pragma: no cover
        raise errors.E_500_INTERNAL_SERVER_ERROR


@router.get(
    "/stats",
    response_model=PlatformStats,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_statistics(su: SuperuserDep) -> PlatformStats:
    resource_type_names = resource_types_mgr.list_names()
    texts = await TextDocument.find_all().to_list()
    text_stats = []

    for text in texts:
        locations_count = await LocationDocument.find(
            LocationDocument.text_id == text.id
        ).count()
        resource_types = {
            rt_name: (
                await ResourceBaseDocument.find(
                    ResourceBaseDocument.text_id == text.id,
                    ResourceBaseDocument.resource_type == rt_name,
                    with_children=True,
                ).count()
            )
            for rt_name in resource_type_names
        }
        resources_count = sum(resource_types.values())
        text_stats.append(
            TextStats(
                id=text.id,
                locations_count=locations_count,
                resources_count=resources_count,
                resource_types=resource_types,
            )
        )

    return PlatformStats(
        users_count=await UserDocument.find_all().count(),
        texts=text_stats,
    )


@router.get(
    "/tasks",
    status_code=status.HTTP_200_OK,
    response_model=list[tasks.TaskRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_all_tasks_status(
    su: SuperuserDep,
) -> list[tasks.TaskDocument]:
    return await tasks.get_tasks(su, get_all=True)


@router.get(
    "/tasks/user",
    status_code=status.HTTP_200_OK,
    response_model=list[tasks.TaskRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_user_tasks_status(
    user: OptionalUserDep,
    pickup_keys: Annotated[
        str | None,
        Header(
            description=(
                "Pickup keys for accessing the tasks in case they "
                "are requested by a non-authenticated user"
            ),
            max_length=1024,
        ),
    ] = None,
) -> list[tasks.TaskDocument]:
    return await tasks.get_tasks(
        user,
        pickup_keys=[pk.strip() for pk in pickup_keys.split(",")]
        if pickup_keys
        else [],
    )


@router.get(
    "/tasks/download",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_EXPORT_NOT_FOUND,
        ]
    ),
)
async def download_task_artifact(
    cfg: ConfigDep,
    pickup_key: Annotated[
        str,
        Query(
            description=("Pickup key for accessing the task's file artifact"),
            alias="pickupKey",
            max_length=64,
        ),
    ],
) -> FileResponse:
    try:
        task: tasks.TaskDocument = (
            await tasks.get_tasks(None, pickup_keys=[pickup_key])
        )[0]
    except Exception:
        raise errors.E_404_EXPORT_NOT_FOUND

    if (
        not task
        or not task.task_type.artifact
        or task.status != "done"
        or not task.result
        or not task.result.get("filename")
        or not task.result.get("artifact")
        or not task.result.get("mimetype")
    ):  # pragma: no cover
        raise errors.E_404_EXPORT_NOT_FOUND

    filename, tempfile_name, mimetype = itemgetter("filename", "artifact", "mimetype")(
        task.result
    )
    # prepare headers ... according to
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
    # the filename should be quoted, but then Safari decides to download the file
    # with a quoted filename :(
    headers = {"Content-Disposition": f"attachment; filename={filename}"}

    return FileResponse(
        path=cfg.temp_files_dir / tempfile_name,
        headers=headers,
        media_type=mimetype,
        background=BackgroundTask(tasks.delete_task, task),
    )


@router.delete(
    "/tasks",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_all_tasks(su: SuperuserDep) -> None:
    await tasks.delete_all_tasks()


@router.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_task(
    task_id: Annotated[PydanticObjectId, Path(alias="id")],
    su: SuperuserDep,
) -> None:
    await tasks.delete_task(await tasks.TaskDocument.get(task_id))
