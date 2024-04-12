import asyncio

from collections.abc import Awaitable
from datetime import datetime
from typing import Annotated, Literal

from beanie import PydanticObjectId
from pydantic import Field

from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin


class Task(ModelBase, ModelFactoryMixin):
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of user who created this task",
        ),
    ]
    label: Annotated[
        str,
        Field(
            description="Label of the task",
        ),
    ]
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
            "user_id",
        ]


async def _run_task(
    task_id: PydanticObjectId, task: Awaitable, *args, **kwargs
) -> None:
    try:
        task_doc: TaskDocument = await TaskDocument.get(task_id)
        await task(*args, **kwargs)
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
    user_id: PydanticObjectId,
    label: str,
    *args,
    **kwargs,
) -> TaskDocument:
    task_doc = await TaskDocument(
        user_id=user_id,
        label=label,
        status="running",
        start_time=datetime.utcnow(),
    ).create()
    asyncio.create_task(_run_task(task_doc.id, task, *args, **kwargs))


async def get_tasks(user_id: PydanticObjectId) -> list[TaskDocument]:
    tasks = await TaskDocument.find(TaskDocument.user_id == user_id).to_list()
    # delete the tasks that are done / have failed
    for task in tasks:
        if task.status == "done" or task.status == "failed":
            await task.delete()
    # return all user tasks
    return tasks
