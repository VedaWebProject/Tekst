import asyncio

from collections.abc import Awaitable
from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Any

from beanie import PydanticObjectId
from beanie.operators import Eq, In
from pydantic import Field

from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin
from tekst.models.user import UserRead


class TaskType(Enum):
    INDEX_CREATE_UPDATE = "index_create_update"
    RESOURCE_IMPORT = "resource_import"
    BROADCAST_USER_NTFC = "broadcast_user_ntfc"
    BROADCAST_ADMIN_NTFC = "broadcast_admin_ntfc"
    CONTENTS_CHANGED_HOOK = "contents_changed_hook"


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
    status: Annotated[
        Literal["waiting", "running", "done", "failed"],
        Field(
            description="Status of the task",
        ),
    ] = "waiting"
    start_time: Annotated[
        datetime | None,
        Field(
            description="Time when the task was started",
        ),
    ] = None
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
            "target_id",
        ]


async def _run_task(
    task: Awaitable,
    task_doc: TaskDocument,
    task_kwargs: dict[str, Any],
) -> None:
    try:
        await task(**task_kwargs)
        task_doc.status = "done"
    except Exception as e:
        task_doc.status = "failed"
        task_doc.error = str(e)
    finally:
        task_doc.end_time = datetime.utcnow()
        task_doc.duration_seconds = (
            task_doc.end_time - task_doc.start_time
        ).total_seconds()
        await task_doc.replace()


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
        status="running",
        start_time=datetime.utcnow(),
    ).create()
    asyncio.create_task(
        _run_task(
            task,
            task_doc,
            task_kwargs,
        )
    )
    return task_doc


async def get_tasks(
    user: UserRead | None,
    *,
    get_all: bool = False,
    delete_finished: bool = False,
) -> list[TaskDocument]:
    # select tasks: get user-specific tasks if initiated by a regular user,
    # get all tasks if initiated by a superuser or None (system-internal)
    tasks = await TaskDocument.find(
        Eq(TaskDocument.user_id, user.id)
        if not get_all or (user and not user.is_superuser)
        else {}
    ).to_list()
    # delete the tasks that are done if delete_finished is True
    if delete_finished:
        for task in tasks:
            if task.status == "done" or task.status == "failed":
                await task.delete()
    # return user tasks
    return tasks


async def is_active(
    task_type: TaskType,
    target_id: PydanticObjectId | None = None,
) -> bool:
    return await TaskDocument.find_one(
        Eq(TaskDocument.task_type, task_type),
        Eq(TaskDocument.target_id, target_id) if target_id else {},
        In(TaskDocument.status, ["waiting", "running"]),
    ).exists()
