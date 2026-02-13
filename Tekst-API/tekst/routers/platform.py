from datetime import UTC, datetime, timedelta
from operator import itemgetter
from typing import Annotated, Union

from beanie import PydanticObjectId
from beanie.operators import NotIn
from fastapi import APIRouter, BackgroundTasks, Header, Path, Query, status
from fastapi.responses import FileResponse
from humps import camelize
from starlette.background import BackgroundTask

from tekst import errors, platform, tasks
from tekst.auth import AccessTokenDocument, OptionalUserDep, SuperuserDep, UserDep
from tekst.config import ConfigDep
from tekst.counters import counter_get, counter_incr
from tekst.models.bookmark import BookmarkDocument
from tekst.models.content import ContentBaseDocument
from tekst.models.correction import CorrectionDocument
from tekst.models.location import LocationDocument
from tekst.models.platform import (
    ClientInitData,
    PlatformData,
    PlatformSecurityInfo,
    PlatformStateDocument,
    PlatformStateRead,
    PlatformStateUpdate,
)
from tekst.models.resource import ResourceBaseDocument
from tekst.models.segment import (
    ClientSegmentCreate,
    ClientSegmentDocument,
    ClientSegmentRead,
    ClientSegmentUpdate,
)
from tekst.models.stats import SuperuserStats, UserStats
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.notifications import send_test_email
from tekst.routers.texts import get_all_texts
from tekst.state import get_state, update_state


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
)


@router.get(
    "",
    response_model=PlatformData,
    status_code=status.HTTP_200_OK,
)
async def get_platform_data(
    ou: OptionalUserDep,
    cfg: ConfigDep,
) -> PlatformData:
    """Returns data about the platform and its configuration"""
    return PlatformData(
        texts=await get_all_texts(ou),
        state=await get_state(),
        security=PlatformSecurityInfo(),
        # find segments with keys starting with "system"
        system_segments=await platform.get_segments(
            system=True,
            user=ou,
        ),
        # find segments with keys not starting with "system"
        info_segments=await platform.get_segments(
            system=False,
            user=ou,
            head_projection=True,
        ),
        tekst=camelize(cfg.tekst),
    )


@router.get(
    "/web-init",
    response_model=ClientInitData,
    status_code=status.HTTP_200_OK,
)
async def get_client_init_data(
    ou: OptionalUserDep,
    cfg: ConfigDep,
) -> PlatformData:
    """Returns data the client needs to initialize"""
    return ClientInitData(
        platform=await get_platform_data(ou, cfg),
        user=ou,
    )


@router.patch(
    "/state",
    response_model=PlatformStateRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_platform_state(
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
    ou: OptionalUserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> ClientSegmentDocument:
    segment = await platform.get_segment(segment_id=segment_id, user=ou)
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
async def get_user_tasks(
    user: OptionalUserDep,
    pickup_keys: Annotated[
        str | None,
        Header(
            description=(
                "Comma-separated pickup keys for accessing the tasks in case they "
                "are requested by a non-authenticated user"
            ),
            max_length=2048,
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


@router.get(
    "/cleanup",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def run_platform_cleanup(su: SuperuserDep) -> tasks.TaskDocument:
    return await tasks.create_task(
        platform.cleanup_task,
        tasks.TaskType.PLATFORM_CLEANUP,
        target_id=tasks.TaskType.PLATFORM_CLEANUP.value,
        user_id=su.id,
    )


@router.get(
    "/test-email",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def send_test_email_to_admin(su: SuperuserDep) -> None:
    await send_test_email(su)


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    response_model=Union[UserStats, SuperuserStats],  # noqa: UP007
)
async def get_stats(
    user: UserDep,
    cfg: ConfigDep,
    background_tasks: BackgroundTasks,
) -> UserStats | SuperuserStats:
    background_tasks.add_task(counter_incr, "stats_requests")
    # collect stats available for any registered user
    stats = UserStats(
        contents=await ContentBaseDocument.find_all(with_children=True).count(),
        locations=await LocationDocument.find_all().count(),
        resources=await ResourceBaseDocument.find_all(with_children=True).count(),
        texts=await TextDocument.find_all().count(),
        users=await UserDocument.find_all().count(),
        active_users_count_past_week=await UserDocument.find(
            UserDocument.last_login >= datetime.now(UTC) - timedelta(days=7)
        ).count(),
        active_users_count_past_month=await UserDocument.find(
            UserDocument.last_login >= datetime.now(UTC) - timedelta(days=30)
        ).count(),
        active_users_count_past_year=await UserDocument.find(
            UserDocument.last_login >= datetime.now(UTC) - timedelta(days=356)
        ).count(),
        search_quick=await counter_get("search_quick"),
        search_advanced=await counter_get("search_advanced"),
        stats_requests=await counter_get("stats_requests"),
    )
    if not user.is_superuser:
        return stats
    # collect stats available for superusers only
    stats = SuperuserStats(
        **stats.model_dump(),
        bookmarks=await BookmarkDocument.find_all().count(),
        corrections=await CorrectionDocument.find_all().count(),
        corrections_all_time=await counter_get("correction_notes"),
        emails=await counter_get("emails"),
        messages=await counter_get("messages_total"),
        messages_user=await counter_get("messages_user"),
        logins=await counter_get("logins"),
        active_sessions=await AccessTokenDocument.find(
            AccessTokenDocument.created_at
            > (datetime.now(UTC) - timedelta(seconds=cfg.security.auth_cookie_lifetime))
        ).count(),
        changed_passwords=await counter_get("changed_passwords"),
        forgotten_passwords=await counter_get("forgotten_passwords"),
        reset_passwords=await counter_get("reset_passwords"),
        deleted_users=await counter_get("deleted_users"),
    )
    return stats
