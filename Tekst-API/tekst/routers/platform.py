from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import NotIn
from fastapi import APIRouter, Path, status

from tekst import errors, locks
from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.config import ConfigDep
from tekst.models.location import LocationDocument
from tekst.models.platform import PlatformData, PlatformStats, TextStats
from tekst.models.resource import ResourceBaseDocument
from tekst.models.segment import (
    ClientSegmentCreate,
    ClientSegmentDocument,
    ClientSegmentHead,
    ClientSegmentRead,
    ClientSegmentUpdate,
)
from tekst.models.settings import (
    PlatformSettingsDocument,
    PlatformSettingsRead,
    PlatformSettingsUpdate,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.resources import resource_types_mgr
from tekst.routers.texts import get_all_texts
from tekst.settings import get_settings
from tekst.tasks import Task, TaskDocument, TaskRead


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
        settings=await get_settings(),
        system_segments=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == True  # noqa: E712
        ).to_list(),
        info_segments=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == False  # noqa: E712
        )
        .project(ClientSegmentHead)
        .to_list(),
    )


@router.patch(
    "/settings",
    response_model=PlatformSettingsRead,
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
    updates: PlatformSettingsUpdate,
) -> PlatformSettingsDocument:
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
    settings_doc = await get_settings()
    return await settings_doc.apply_updates(updates)


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
    "/locks/{key}",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_lock_status(
    su: SuperuserDep, lock_key: Annotated[locks.LockKey, Path(alias="key")]
) -> bool:
    return await locks.is_locked(lock_key)


@router.get(
    "/locks",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_locks_status(su: SuperuserDep) -> dict[str, bool]:
    return await locks.get_locks_status()


@router.delete(
    "/locks",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def release_locks(su: SuperuserDep) -> None:
    for lk in locks.LockKey:
        await locks.release(lk)


@router.get(
    "/tasks",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_tasks_status(user: UserDep) -> list[TaskDocument]:
    return await Task.get_tasks(user.id)
