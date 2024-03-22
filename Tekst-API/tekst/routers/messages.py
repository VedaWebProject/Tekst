from datetime import datetime
from typing import Annotated, Literal

from beanie.operators import And, Eq, In, Or, Set
from fastapi import APIRouter, Path, status

from tekst import errors
from tekst.auth import (
    UserDep,
)
from tekst.models.common import PydanticObjectId
from tekst.models.message import MessageCreate, MessageDocument, MessageRead
from tekst.models.user import UserDocument, UserReadPublic


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[MessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_404_USER_NOT_FOUND,
        ]
    ),
)
async def send_message(
    user: UserDep,
    message: MessageCreate,
) -> list[MessageRead]:
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
    await MessageDocument.model_from(message).create()
    return await get_messages(user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[MessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def get_messages(user: UserDep) -> list[MessageRead]:
    """Returns all messages for/from the requesting user"""
    messages = await MessageDocument.find(
        Or(
            MessageDocument.recipient == user.id,
            MessageDocument.sender == user.id,
        ),
        MessageDocument.deleted != user.id,
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

    # make messages list contain MessageRead instaces with user data
    messages: list[MessageRead] = [
        MessageRead(
            **dict(
                sender_user=users.get(m.sender, "system"),
                recipient_user=users.get(m.recipient, None),
                **m.model_dump(),
            )
        )
        for m in messages
    ]

    return messages


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[MessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_404_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_message(
    user: UserDep, message_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> list[MessageRead]:
    """Deletes the message with the given ID"""
    msg: MessageDocument = await MessageDocument.get(message_id)

    # check if message exists
    if not msg:
        raise errors.E_404_NOT_FOUND

    # check if requesting user can delete message
    if user.id != msg.sender and user.id != msg.recipient:
        raise errors.E_403_FORBIDDEN

    # mark message as deleted or actually delete it depending on current deletion status
    if not msg.sender or (msg.deleted and msg.deleted != user.id):
        await msg.delete()
    else:
        msg.deleted = user.id
        await msg.replace()

    return await get_messages(user)


@router.delete(
    "/threads/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[MessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def delete_thread(
    user: UserDep,
    sender_id: Annotated[PydanticObjectId | Literal["system"], Path(alias="id")],
) -> list[MessageRead]:
    """
    Marks all received messages from the given user as deleted or actually deletes them,
    depending on the current deletion status
    """
    for msg in await MessageDocument.find(
        Or(
            And(
                Eq(
                    MessageDocument.sender, None if sender_id == "system" else sender_id
                ),
                Eq(MessageDocument.recipient, user.id),
            ),
            And(
                Eq(MessageDocument.sender, user.id),
                Eq(MessageDocument.recipient, sender_id),
            ),
        )
    ).to_list():
        await delete_message(user, msg.id)
    return await get_messages(user)


@router.post(
    "/threads/{id}/read",
    status_code=status.HTTP_200_OK,
    response_model=list[MessageRead],
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def mark_thread_read(
    user: UserDep,
    sender_id: Annotated[PydanticObjectId | Literal["system"], Path(alias="id")],
) -> list[MessageRead]:
    """Marks all received messages from the given user as read"""
    await MessageDocument.find(
        Eq(MessageDocument.sender, None if sender_id == "system" else sender_id),
        Eq(MessageDocument.recipient, user.id),
    ).update(Set({MessageDocument.read: True}))
    return await get_messages(user)
