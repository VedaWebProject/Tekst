from typing import Annotated

from pydantic import Field, StringConstraints, field_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.utils import validators as val
from tekst.utils.strings import cleanup_spaces_multiline


class Bookmark(ModelBase, ModelFactoryMixin):
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of user who created this bookmark",
        ),
    ]
    text_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of text this bookmark belongs to",
        ),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text location this bookmark refers to",
        ),
    ]
    level: Annotated[
        int,
        Field(
            ge=0,
            description="Text level this bookmark refers to",
        ),
    ]
    position: Annotated[
        int,
        Field(
            ge=0,
            description="Position of the text location this bookmark refers to",
        ),
    ]
    location_labels: Annotated[
        list[str],
        Field(
            description="Text location labels from root to target location",
        ),
    ]
    comment: Annotated[
        str | None,
        Field(
            description="Comment associated with this bookmark",
        ),
        StringConstraints(
            max_length=1000,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
        val.EmptyStringToNone,
    ] = None

    @field_validator("comment", mode="after")
    @classmethod
    def format_comment(cls, v) -> str | None:
        return cleanup_spaces_multiline(v) or None


class BookmarkDocument(Bookmark, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "bookmarks"
        indexes = [
            "user_id",
        ]


BookmarkRead = Bookmark.read_model()


class BookmarkCreate(ModelBase):
    location_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text location this bookmark refers to",
        ),
    ]
    comment: Annotated[
        str | None,
        Field(
            description="Comment associated with this bookmark",
        ),
        StringConstraints(
            max_length=1000,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
        val.EmptyStringToNone,
    ] = None
