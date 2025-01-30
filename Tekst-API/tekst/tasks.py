import asyncio

from collections.abc import Awaitable
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import LT, NE, Eq, In
from fastapi.encoders import jsonable_encoder
from pydantic import Field

from tekst import errors
from tekst.config import TekstConfig, get_config
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin
from tekst.models.user import UserRead
from tekst.types import ConStr, ConStrOrNone


class TaskType(Enum):
    """
    Task types with locking and artifact flags
    """

    INDICES_CREATE_UPDATE = "indices_create_update", True, False
    RESOURCE_IMPORT = "resource_import", True, False
    RESOURCE_EXPORT = "resource_export", True, True
    SEARCH_EXPORT = "search_export", True, True
    BROADCAST_USER_NTFC = "broadcast_user_ntfc", False, False
    BROADCAST_ADMIN_NTFC = "broadcast_admin_ntfc", False, False
    RESOURCE_MAINTENANCE_HOOK = "resource_maintenance_hook", True, False
    STRUCTURE_UPDATE = "structure_update", True, False

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, locking: bool, artifact: bool):
        self._locking_ = locking
        self._artifact_ = artifact

    def __str__(self):
        return self.value

    @property
    def locking(self):
        return self._locking_

    @property
    def artifact(self):
        return self._artifact_


class Task(ModelBase, ModelFactoryMixin):
    task_type: Annotated[
        TaskType,
        Field(
            description="Type of the task",
            alias="type",
        ),
    ]
    target_id: Annotated[
        PydanticObjectId | ConStrOrNone(),
        Field(
            description="ID of the target of the task or None if there is no target",
        ),
    ] = None
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of user who created this task",
        ),
    ]
    pickup_key: Annotated[
        ConStr(
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
        ConStrOrNone(),
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
    task_doc: TaskDocument,
    task_kwargs: dict[str, Any] = {},
) -> None:
    op_id = log_op_start(
        f"Run task {str(task_doc.id)} of type {task_doc.task_type} "
        f"with target ID {str(task_doc.target_id)}"
    )
    try:
        if await is_locked(task_doc.task_type, task_doc.id, task_doc.target_id):
            log.warning(
                f"Task '{task_doc.task_type.value}' with target ID "
                f"{task_doc.target_id} already running. Task will be ended as 'failed'."
            )
            raise errors.E_409_ACTION_LOCKED
        result = await task(**task_kwargs)
        task_doc.status = "done"
        log_op_end(op_id)
        try:
            task_doc.result = jsonable_encoder(result)
        except Exception as _:  # pragma: no cover
            task_doc.result = {"msg": str(result)}
            log.warning(f"Could not JSON encode task result for task: {str(task_doc)}")
    except Exception as e:
        log_op_end(op_id, failed=True)
        task_doc.status = "failed"
        try:
            task_doc.error = e.detail.detail.key
        except Exception:  # pragma: no cover
            task_doc.error = str(e)
    finally:
        task_doc.end_time = datetime.utcnow()
        task_doc.duration_seconds = (
            task_doc.end_time - task_doc.start_time
        ).total_seconds()
        await task_doc.save()
        # if this task produced an artifact, automatically
        # delete it after the configured time
        if task_doc.task_type.artifact:
            _auto_delete_task_delayed(task_doc)


async def create_task(
    task: Awaitable,
    task_type: TaskType,
    *,
    target_id: PydanticObjectId | str | None = None,
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
            task_doc=task_doc,
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
    # (excluding artifact-producing tasks, because these are still
    # needed for locating the generated artifacts/files)
    if user and not get_all:
        for task in tasks:
            if (
                task.status in ("done", "failed")
                and task.user_id is not None
                and (not task.task_type.artifact or task.status == "failed")
            ):
                await delete_task(task)
    return tasks


async def is_locked(
    task_type: TaskType,
    task_id: PydanticObjectId,
    target_id: PydanticObjectId | str | None = None,
) -> bool:
    if not task_type.locking:
        return False
    return await TaskDocument.find_one(
        NE(TaskDocument.id, task_id),
        Eq(TaskDocument.task_type, task_type),
        Eq(TaskDocument.target_id, target_id) if target_id else {},
        In(TaskDocument.status, ["waiting", "running"]),
    ).exists()


async def delete_task(task_doc: TaskDocument | None) -> None:
    if not task_doc:  # pragma: no cover
        return
    if task_doc.result and task_doc.result.get("artifact"):
        cfg: TekstConfig = get_config()
        tempfile_path = cfg.temp_files_dir / task_doc.result["artifact"]
        tempfile_path.unlink(missing_ok=True)
    await task_doc.delete()


async def delete_all_tasks() -> None:
    for task in await TaskDocument.find_all().to_list():
        await delete_task(task)


async def cleanup_tasks() -> None:
    # delete all tasks that started more than 1 week ago
    for task in await TaskDocument.find(
        NE(TaskDocument.task_type, TaskType.RESOURCE_EXPORT),
        LT(TaskDocument.start_time, datetime.utcnow() - timedelta(weeks=1)),
    ).to_list():
        await delete_task(task)  # pragma: no cover


async def _auto_delete_task_delayed_task(task_doc: TaskDocument) -> None:
    cfg: TekstConfig = get_config()
    await asyncio.sleep(cfg.misc.del_exports_after_minutes * 60)
    await delete_task(task_doc)  # pragma: no cover


def _auto_delete_task_delayed(task_doc: TaskDocument) -> None:
    asyncio.create_task(
        _auto_delete_task_delayed_task(task_doc),
    )
