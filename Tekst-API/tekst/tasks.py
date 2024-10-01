import asyncio
import gc

from collections.abc import Awaitable
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import LT, NE, Eq, In
from fastapi.encoders import jsonable_encoder
from pydantic import Field, StringConstraints

from tekst import errors
from tekst.config import TekstConfig, get_config
from tekst.logs import log
from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin
from tekst.models.user import UserRead


class TaskType(Enum):
    INDICES_CREATE_UPDATE = "indices_create_update"
    RESOURCE_IMPORT = "resource_import"
    RESOURCE_EXPORT = "resource_export"
    BROADCAST_USER_NTFC = "broadcast_user_ntfc"
    BROADCAST_ADMIN_NTFC = "broadcast_admin_ntfc"
    RESOURCE_MAINTENANCE_HOOK = "resource_maintenance_hook"
    STRUCTURE_UPDATE = "structure_update"


_task_type_props = {
    TaskType.INDICES_CREATE_UPDATE: {"locking": True},
    TaskType.RESOURCE_IMPORT: {"locking": True},
    TaskType.RESOURCE_EXPORT: {"locking": False},
    TaskType.BROADCAST_USER_NTFC: {"locking": False},
    TaskType.BROADCAST_ADMIN_NTFC: {"locking": False},
    TaskType.RESOURCE_MAINTENANCE_HOOK: {"locking": True},
    TaskType.STRUCTURE_UPDATE: {"locking": True},
}


class Task(ModelBase, ModelFactoryMixin):
    task_type: Annotated[
        TaskType,
        Field(
            description="Type of the task",
            alias="type",
        ),
    ]
    target_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the target of the task or None if there is no target",
        ),
    ] = None
    user_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of user who created this task",
        ),
    ] = None
    pickup_key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=64,
        ),
        Field(
            description=(
                "Pickup key for accessing the task in case tasks "
                "are requested by a non-authenticated user"
            ),
        ),
    ]
    status: Annotated[
        Literal["waiting", "running", "done", "failed"],
        Field(
            description="Status of the task",
        ),
    ]
    start_time: Annotated[
        datetime,
        Field(
            description="Time when the task was started",
        ),
    ]
    end_time: Annotated[
        datetime | None,
        Field(
            description="Time when the task has ended",
        ),
    ] = None
    duration_seconds: Annotated[
        float | None,
        Field(
            description="Duration of the finished task in seconds",
        ),
    ] = None
    result: Annotated[
        dict[str, Any] | None,
        Field(
            description="Result data of the task",
        ),
    ] = None
    error: Annotated[
        str | None,
        Field(
            description="Error message if the task failed",
        ),
    ] = None


TaskRead = Task.read_model()


class TaskDocument(Task, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "tasks"
        indexes = [
            "task_type",
            "user_id",
            "pickup_key",
            "target_id",
        ]


async def _run_task(
    *,
    task: Awaitable,
    task_type: TaskType,
    task_doc: TaskDocument,
    target_id: PydanticObjectId | None = None,
    task_kwargs: dict[str, Any] = {},
) -> None:
    try:
        if await is_locked(task_type, task_doc.id, target_id):
            log.warning(
                f"Task '{task_type.value}' with target ID "
                f"{target_id} already running. Task will be ended as 'failed'."
            )
            raise errors.E_409_ACTION_LOCKED
        result = await task(**task_kwargs)
        task_doc.status = "done"
        try:
            task_doc.result = jsonable_encoder(result)
        except Exception as _:
            log.debug(f"Could not encode task result for task: {str(task)}")
    except Exception as e:
        task_doc.status = "failed"
        log.error(
            f"Task '{task_type.value}' with target ID {target_id} failed: {str(e)}"
        )
        try:
            task_doc.error = e.detail.detail.key
        except Exception:
            task_doc.error = str(e)
    finally:
        task_doc.end_time = datetime.utcnow()
        task_doc.duration_seconds = (
            task_doc.end_time - task_doc.start_time
        ).total_seconds()
        await task_doc.save()
        del task, task_doc
        gc.collect()


async def create_task(
    task: Awaitable,
    task_type: TaskType,
    *,
    target_id: PydanticObjectId | None = None,
    user_id: PydanticObjectId | None = None,
    task_kwargs: dict[str, Any] = {},
) -> TaskDocument:
    task_doc = await TaskDocument(
        task_type=task_type,
        target_id=target_id,
        user_id=user_id,
        pickup_key=str(uuid4()),
        status="running",
        start_time=datetime.utcnow(),
    ).create()
    asyncio.create_task(
        _run_task(
            task=task,
            task_type=task_type,
            task_doc=task_doc,
            target_id=target_id,
            task_kwargs=task_kwargs,
        )
    )
    return task_doc


async def get_tasks(
    user: UserRead | None,
    *,
    pickup_keys: list[str] = [],
    get_all: bool = False,
) -> list[TaskDocument]:
    # run tasks cleanup first
    await cleanup_tasks()
    # select tasks: get user-specific tasks if initiated by a regular user,
    # get all tasks if initiated by a superuser or None (system-internal)
    if not user:
        # non-authenticated user: needs pickup key(s)
        query = In(TaskDocument.pickup_key, pickup_keys)
    elif user.is_superuser and get_all:
        # superuser that wants ALL tasks: just return everything
        query = {}
    else:
        # regular user or superuser that wants only user-specific tasks
        query = Eq(TaskDocument.user_id, user.id)
    tasks = await TaskDocument.find(query).to_list()
    # delete retrieved user tasks that are done/failed
    # (excluding successful exports, because these are still
    # needed for locating generated files)
    if user and not get_all:
        for task in tasks:
            if (
                task.status in ["done", "failed"]
                and task.user_id is not None
                and (
                    task.task_type != TaskType.RESOURCE_EXPORT
                    or task.status == "failed"
                )
            ):
                await delete_task(task)
    return tasks


async def is_locked(
    task_type: TaskType,
    task_id: PydanticObjectId,
    target_id: PydanticObjectId | None = None,
) -> bool:
    if not _task_type_props[task_type]["locking"]:
        return False
    return await TaskDocument.find_one(
        NE(TaskDocument.id, task_id),
        Eq(TaskDocument.task_type, task_type),
        Eq(TaskDocument.target_id, target_id) if target_id else {},
        In(TaskDocument.status, ["waiting", "running"]),
    ).exists()


async def delete_task(task: TaskDocument) -> None:
    if not task:
        return
    if task.result and "artifact" in task.result:
        cfg: TekstConfig = get_config()
        tempfile_path = cfg.temp_files_dir / task.result["artifact"]
        tempfile_path.unlink(missing_ok=True)
    await task.delete()


async def delete_system_tasks() -> None:
    for task in await TaskDocument.find(Eq(TaskDocument.user_id, None)).to_list():
        await delete_task(task)


async def delete_all_tasks() -> None:
    for task in await TaskDocument.find_all().to_list():
        await delete_task(task)


async def cleanup_tasks() -> None:
    # delete export tasks that started min. 30 minutes ago
    for task in await TaskDocument.find(
        Eq(TaskDocument.task_type, TaskType.RESOURCE_EXPORT),
        LT(TaskDocument.start_time, datetime.utcnow() - timedelta(minutes=30)),
    ).to_list():
        await delete_task(task)
    # delete all other tasks that started more than 1 week ago
    for task in await TaskDocument.find(
        NE(TaskDocument.task_type, TaskType.RESOURCE_EXPORT),
        LT(TaskDocument.start_time, datetime.utcnow() - timedelta(weeks=1)),
    ).to_list():
        await delete_task(task)
