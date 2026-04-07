from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    PydanticObjectId,
    ReadBase,
)
from tekst.types import FalsyToNone, MultiLineString


class Bookmark(ModelBase):
    user_id: Annotated[
        PydanticObjectId,
        Field(description="ID of user who created this bookmark"),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    text_id: Annotated[
        PydanticObjectId,
        Field(description="ID of text this bookmark belongs to"),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the text location this bookmark refers to"),
        ExcludeFromModelVariants(update=True),
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
        Field(description="Text location labels from root to target location"),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]
    comment: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=1000),
        MultiLineString,
        FalsyToNone,
        Field(description="Comment associated with this bookmark"),
        ExcludeFromModelVariants(update=True),
    ] = None


class BookmarkDocument(Bookmark, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "bookmarks"
        indexes = ["user_id"]


class BookmarkRead(Bookmark, ReadBase):
    pass


class BookmarkCreate(Bookmark, CreateBase):
    pass
