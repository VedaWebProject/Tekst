from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Path, status

from tekst import errors, locks, search
from tekst.auth import SuperuserDep
from tekst.models.location import LocationDocument
from tekst.models.platform import PlatformStats, TextStats
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument, UserRead
from tekst.resources import resource_types_mgr
from tekst.models.search import IndexInfoResponse


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)


# ROUTES DEFINITIONS...


@router.get(
    "/stats",
    response_model=PlatformStats,
    status_code=status.HTTP_200_OK,
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
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_users(su: SuperuserDep) -> list[UserDocument]:
    return await UserDocument.find_all().to_list()


@router.get(
    "/index/create",
    status_code=status.HTTP_202_ACCEPTED,
    responses=errors.responses(
        [
            errors.E_409_ACTION_LOCKED,
        ]
    ),
)
async def create_search_index(
    su: SuperuserDep, background_tasks: BackgroundTasks
) -> None:
    if await locks.is_locked(locks.LockKey.INDEX_CREATE_UPDATE):
        raise errors.E_409_ACTION_LOCKED
    background_tasks.add_task(search.create_index)


@router.get(
    "/index/info",
    response_model=IndexInfoResponse,
    status_code=status.HTTP_200_OK,
)
async def get_search_index_info(su: SuperuserDep) -> IndexInfoResponse:
    return await search.get_index_info()


@router.get(
    "/locks/{key}",
    status_code=status.HTTP_200_OK,
)
async def get_lock_status(
    su: SuperuserDep, lock_key: Annotated[locks.LockKey, Path(alias="key")]
) -> bool:
    return await locks.is_locked(lock_key)


@router.get(
    "/locks",
    status_code=status.HTTP_200_OK,
)
async def get_locks_status(su: SuperuserDep) -> dict[str, bool]:
    return await locks.get_locks_status()


@router.delete(
    "/locks",
    status_code=status.HTTP_200_OK,
)
async def release_locks(su: SuperuserDep) -> None:
    for lk in locks.LockKey:
        await locks.release(lk)
