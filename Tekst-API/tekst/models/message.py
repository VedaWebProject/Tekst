from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.models.user import UserReadPublic
from tekst.utils import validators as val


class UserMessage(ModelBase, ModelFactoryMixin):
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
        ExcludeFromModelVariants(create=True),
    ] = None
    read: Annotated[
        bool,
        Field(
            description="Whether the message has been read by the recipient",
        ),
        ExcludeFromModelVariants(create=True),
    ] = False
    deleted: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the user who deleted the message or None if not deleted",
        ),
        ExcludeFromModelVariants(create=True),
    ] = None


class UserMessageDocument(UserMessage, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "messages"
        indexes = [
            "recipient",
            "sender",
        ]


UserMessageRead = UserMessage.read_model()
UserMessageCreate = UserMessage.create_model()


class UserMessageThread(ModelBase):
    id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the thread or None if the message is a system message"
        ),
    ]
    contact: Annotated[
        UserReadPublic | None,
        Field(
            description="User data for the other user participating in this thread",
        ),
    ]
    unread: Annotated[
        int,
        Field(
            description="Number of unread messages in this thread",
        ),
    ]
