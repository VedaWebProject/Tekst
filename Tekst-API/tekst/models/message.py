from typing import Annotated

from pydantic import AwareDatetime, Field, StringConstraints

from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    PydanticObjectId,
    ReadBase,
)
from tekst.models.user import UserReadPublic
from tekst.types import MultiLineString


class UserMessage(ModelBase):
    sender: Annotated[
        PydanticObjectId | None,
        Field(description="ID of the sender or None if this is a system message"),
    ] = None
    recipient: Annotated[
        PydanticObjectId,
        Field(description="ID of the recipient"),
    ]
    content: Annotated[
        str,
        StringConstraints(min_length=1, max_length=1000),
        MultiLineString,
        Field(description="Content of the message"),
    ]
    created_at: Annotated[
        AwareDatetime,
        Field(description="Time when the message was sent"),
        ExcludeFromModelVariants(create=True),
    ]
    read: Annotated[
        bool,
        Field(description="Whether the message has been read by the recipient"),
        ExcludeFromModelVariants(create=True),
    ] = False
    deleted: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the user who deleted the message or None if not deleted"
        ),
        ExcludeFromModelVariants(create=True),
    ] = None


class UserMessageDocument(UserMessage, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "messages"
        indexes = [
            [
                "recipient",
                "sender",
            ]
        ]


class UserMessageRead(UserMessage, ReadBase):
    pass


class UserMessageCreate(UserMessage, CreateBase):
    pass


class UserMessageThread(ModelBase):
    id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the thread or None if the message is a system message"
        ),
    ]
    contact: Annotated[
        UserReadPublic | None,
        Field(description="User data for the other user participating in this thread"),
    ]
    unread: Annotated[
        int,
        Field(description="Number of unread messages in this thread"),
    ]
