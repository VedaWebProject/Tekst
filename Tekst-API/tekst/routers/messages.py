from datetime import datetime, timedelta
from typing import Annotated, Literal

from beanie import PydanticObjectId
from beanie.operators import LT, And, Eq, In, Or, Set
from fastapi import APIRouter, Depends, Path, Query, status

from tekst import errors
from tekst.auth import (
    UserDep,
)
from tekst.config import TekstConfig, get_config
from tekst.models.message import (
    UserMessageCreate,
    UserMessageDocument,
    UserMessageRead,
    UserMessageThread,
)
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.notifications import TemplateIdentifier, send_notification
from tekst.settings import get_settings


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserMessageRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_404_USER_NOT_FOUND,
        ]
    ),
)
async def send_message(
    user: UserDep,
    message: UserMessageCreate,
) -> UserMessageRead:
    """Creates a message for the specified recipient"""
    # check if sender == recipient
    if user.id == message.recipient:
        raise errors.E_400_MESSAGE_TO_SELF

    # check if recipient exists
    if not await UserDocument.find_one(
        UserDocument.id == message.recipient,
        Eq(UserDocument.is_active, True),
    ).exists():
        raise errors.E_404_USER_NOT_FOUND

    # force some message values
    message.sender = user.id
    message.time = datetime.utcnow()
    message.deleted = None
    message.read = False

    # create message
    message_doc = await UserMessageDocument.model_from(message).create()

    # send notification email to recipient
    if (
        TemplateIdentifier.EMAIL_MESSAGE_RECEIVED.value
        in user.user_notification_triggers
    ):
        await send_notification(
            to_user=UserRead.model_from(await UserDocument.get(message.recipient)),
            template_id=TemplateIdentifier.EMAIL_MESSAGE_RECEIVED,
            username=user.name if "name" in user.public_fields else user.username,
            message_content=message.content,
        )

    # return created message
    return message_doc


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[UserMessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_thread_messages(
    user: UserDep,
    cfg: Annotated[TekstConfig, Depends(get_config)],
    thread_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="thread",
            description="ID of the thread to return messages for",
        ),
    ] = None,
) -> list[UserMessageRead]:
    """Returns all messages belonging to the specified thread"""

    # trigger housekeeping: delete old messages according to config (for all users!)
    await UserMessageDocument.find(
        LT(
            UserMessageDocument.time,
            datetime.utcnow() - timedelta(days=cfg.misc.usrmsg_force_delete_after_days),
        ),
    ).delete()

    # find messages belonging to this thread
    messages = (
        await UserMessageDocument.find(
            Or(
                And(
                    UserMessageDocument.recipient == user.id,
                    UserMessageDocument.sender == thread_id,
                ),
                And(
                    UserMessageDocument.recipient == thread_id,
                    UserMessageDocument.sender == user.id,
                ),
            ),
            UserMessageDocument.deleted != user.id,
        )
        .sort(+UserMessageDocument.time)
        .to_list()
    )

    # mark received messages in this thread as read
    await UserMessageDocument.find(
        Eq(UserMessageDocument.sender, thread_id),
        Eq(UserMessageDocument.recipient, user.id),
    ).update(Set({UserMessageDocument.read: True}))

    return messages


@router.get(
    "/threads",
    status_code=status.HTTP_200_OK,
    response_model=list[UserMessageThread],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_threads(
    user: UserDep,
) -> list[UserMessageThread]:
    """Returns all message threads involving the requesting user"""
    messages = await UserMessageDocument.find(
        Or(
            UserMessageDocument.recipient == user.id,
            UserMessageDocument.sender == user.id,
        ),
        UserMessageDocument.deleted != user.id,
    ).to_list()

    # get user IDs of all senders/recipients
    user_ids = set()
    for user_id_pair in [[m.sender, m.recipient] for m in messages]:
        user_ids.update([uid for uid in user_id_pair if uid])

    # get all relevant users
    users = {
        u.id: UserReadPublic(**u.model_dump(exclude={"bio"}))
        for u in await UserDocument.find(
            In(UserDocument.id, list(user_ids)),
        ).to_list()
    }

    # group messages as threads by contact
    threads = dict()
    platform_name = (await get_settings()).platform_name
    for msg_doc in messages:
        msg = UserMessageRead.model_from(msg_doc)
        contact_id = msg.sender if msg.sender != user.id else msg.recipient
        if contact_id not in threads:
            contact: UserReadPublic = users.get(contact_id) or UserReadPublic(
                id=PydanticObjectId(),
                username="system",
                name=platform_name,
                is_active=True,
                is_superuser=False,
                public_fields=["name"],
            )
            threads[contact_id] = UserMessageThread(
                id=contact_id,
                contact=contact,
                unread=1 if msg.recipient == user.id and not msg.read else 0,
            )
        else:
            threads[contact_id].unread += (
                1 if msg.recipient == user.id and not msg.read else 0
            )

    return threads.values()


@router.delete(
    "/threads/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_404_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_thread(
    user: UserDep,
    thread_id: Annotated[PydanticObjectId | Literal["system"], Path(alias="id")],
) -> None:
    """
    Marks all received messages from the given user as deleted or actually deletes them,
    depending on the current deletion status
    """
    thread_id = (
        thread_id if thread_id != "system" else None
    )  # system threads don't have a thread (sender) ID
    for msg in await UserMessageDocument.find(
        Or(
            And(
                Eq(
                    UserMessageDocument.sender,
                    thread_id,
                ),
                Eq(UserMessageDocument.recipient, user.id),
            ),
            And(
                Eq(UserMessageDocument.sender, user.id),
                Eq(UserMessageDocument.recipient, thread_id),
            ),
        )
    ).to_list():
        # check if message exists
        if not msg:
            raise errors.E_404_NOT_FOUND

        # check if requesting user can delete message
        if user.id != msg.sender and user.id != msg.recipient:
            raise errors.E_403_FORBIDDEN

        # mark message as deleted or actually
        # delete it depending on current deletion status
        if not msg.sender or (msg.deleted and msg.deleted != user.id):
            await msg.delete()
        else:
            msg.deleted = user.id
            await msg.replace()
