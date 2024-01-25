from typing import Annotated

from pydantic import StringConstraints

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)


class Bookmark(ModelBase, ModelFactoryMixin):
    user_id: PydanticObjectId
    text_id: PydanticObjectId
    location_id: PydanticObjectId
    level: int
    position: int
    label: str
    comment: Annotated[str | None, StringConstraints(max_length=1000)] = None


class BookmarkDocument(Bookmark, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "bookmarks"
        indexes = ["user_id"]


BookmarkRead = Bookmark.read_model()


class BookmarkCreate(ModelBase):
    location_id: PydanticObjectId
    comment: Annotated[str | None, StringConstraints(max_length=1000)] = None
