from typing import Annotated

from pydantic import StringConstraints, field_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.utils.strings import remove_excess_spaces


class Bookmark(ModelBase, ModelFactoryMixin):
    user_id: PydanticObjectId
    text_id: PydanticObjectId
    location_id: PydanticObjectId
    level: int
    position: int
    location_labels: list[str]
    comment: Annotated[
        str | None, StringConstraints(max_length=1000, strip_whitespace=True)
    ] = None

    @field_validator("comment", mode="after")
    @classmethod
    def format_comment(cls, v):
        return remove_excess_spaces(v)


class BookmarkDocument(Bookmark, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "bookmarks"
        indexes = ["user_id"]


BookmarkRead = Bookmark.read_model()


class BookmarkCreate(ModelBase):
    location_id: PydanticObjectId
    comment: Annotated[str | None, StringConstraints(max_length=1000)] = None
