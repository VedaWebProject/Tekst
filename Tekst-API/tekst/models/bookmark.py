from typing import Annotated

from pydantic import StringConstraints, field_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.utils import validators as val
from tekst.utils.strings import cleanup_spaces_multiline


class Bookmark(ModelBase, ModelFactoryMixin):
    user_id: PydanticObjectId
    text_id: PydanticObjectId
    location_id: PydanticObjectId
    level: int
    position: int
    location_labels: list[str]
    comment: Annotated[
        str | None,
        StringConstraints(max_length=1000, strip_whitespace=True),
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
        indexes = ["user_id"]


BookmarkRead = Bookmark.read_model()


class BookmarkCreate(ModelBase):
    location_id: PydanticObjectId
    comment: Annotated[
        str | None,
        StringConstraints(max_length=1000),
        val.CleanupMultiline,
        val.EmptyStringToNone,
    ] = None
