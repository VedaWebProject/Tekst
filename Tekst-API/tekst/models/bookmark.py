from typing import Annotated

from pydantic import Field, field_validator

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.types import ConStrOrNone
from tekst.utils.strings import cleanup_spaces_multiline


class Bookmark(ModelBase, ModelFactoryMixin):
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of user who created this bookmark",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    text_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of text this bookmark belongs to",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text location this bookmark refers to",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]
    level: Annotated[
        int,
        Field(
            ge=0,
            description="Text level this bookmark refers to",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    position: Annotated[
        int,
        Field(
            ge=0,
            description="Position of the text location this bookmark refers to",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    location_labels: Annotated[
        list[str],
        Field(
            description="Text location labels from root to target location",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    comment: Annotated[
        ConStrOrNone(
            max_length=1000,
            cleanup="multiline",
        ),
        Field(
            description="Comment associated with this bookmark",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
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
BookmarkCreate = Bookmark.create_model()
