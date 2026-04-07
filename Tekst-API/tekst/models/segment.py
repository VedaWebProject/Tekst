from typing import Annotated, Literal

from beanie import PydanticObjectId
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)

from tekst.i18n import TranslationLocaleKey
from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ModelBase,
    ReadBase,
    make_update_model,
)
from tekst.types import SingleLineString


class ClientSegment(ModelBase):
    key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            pattern=r"[a-zA-Z0-9\-_]+",
        ),
        Field(
            description=(
                "Key of this segment. System segment keys must start with `system`."
            ),
        ),
    ]

    editor_mode: Annotated[
        Literal["wysiwyg", "html"],
        Field(description="Last used editor mode"),
    ] = "wysiwyg"

    locale: Annotated[
        TranslationLocaleKey,
        Field(description="Locale indicating the translation language of this segment"),
    ]

    restriction: Annotated[
        Literal["none", "user", "superuser"],
        Field(
            description=(
                "Whether access is unrestricted or restricted to superusers or users"
            ),
        ),
    ] = "none"

    title: Annotated[
        str,
        StringConstraints(min_length=1, max_length=32),
        SingleLineString,
        Field(description="Title of this segment"),
    ]

    sort_order: Annotated[
        int,
        Field(
            description=(
                "Sort order for displaying this segment among others "
                "(only relevant for non-system segments aka. info pages!)"
            ),
            ge=0,
            le=1000,
        ),
    ] = 10

    html: Annotated[
        str,
        StringConstraints(max_length=1048576),
        Field(description="HTML content of this segment"),
    ]


class ClientSegmentDocument(ClientSegment, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "segments"
        indexes = [
            [
                "key",
                "locale",
            ]
        ]


class ClientSegmentCreate(ClientSegment, CreateBase):
    pass


class ClientSegmentRead(ClientSegment, ReadBase):
    pass


ClientSegmentUpdate = make_update_model(ClientSegment)


class ClientSegmentSignature(BaseModel):
    class Settings:
        projection = {
            "id": "$_id",
            "key": 1,
            "title": 1,
            "locale": 1,
        }

    id: PydanticObjectId
    key: str
    title: str | None = None
    locale: TranslationLocaleKey
