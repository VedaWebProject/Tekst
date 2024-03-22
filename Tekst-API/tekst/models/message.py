from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
    ReadBase,
)
from tekst.models.user import UserReadPublic
from tekst.utils import validators as val


class Message(ModelBase, ModelFactoryMixin):
    sender: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the sender or None if this is a system message",
        ),
    ] = None
    recipient: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the recipient",
        ),
    ]
    content: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=1000,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
        Field(
            description="Content of the message",
        ),
    ]
    time: Annotated[
        datetime | None,
        Field(
            description="Time when the message was sent",
        ),
    ] = None
    read: Annotated[
        bool,
        Field(
            description="Whether the message has been read by the recipient",
        ),
    ] = False
    deleted: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the user who deleted the message or None if not deleted",
        ),
    ] = None


class MessageDocument(Message, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "messages"
        indexes = [
            "recipient",
            "sender",
        ]


class MessageRead(Message, ReadBase):
    sender_user: UserReadPublic | None
    recipient_user: UserReadPublic


MessageCreate = Message.create_model()
