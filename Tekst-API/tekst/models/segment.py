from typing import Annotated, Any, Literal

from beanie import PydanticObjectId
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    field_validator,
)

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    TranslationLocaleKey,
)
from tekst.utils import validators as val


class ClientSegment(ModelBase, ModelFactoryMixin):
    key: Annotated[
        str,
        Field(
            description=(
                "Key of this segment. System segment keys must start with `system`."
            ),
        ),
        StringConstraints(
            min_length=1,
            max_length=32,
            pattern=r"[a-zA-Z0-9\-_]+",
            strip_whitespace=True,
        ),
    ]
    editor_mode: Annotated[
        Literal["wysiwyg", "html"],
        Field(
            description="Last used editor mode",
        ),
    ] = "wysiwyg"
    locale: Annotated[
        TranslationLocaleKey,
        Field(
            description="Locale indicating the translation language of this segment",
        ),
    ]
    title: Annotated[
        str | None,
        StringConstraints(
            max_length=32,
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
        Field(
            description="Title of this segment",
        ),
    ] = None
    html: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=1048576,
            strip_whitespace=True,
        ),
        Field(
            description="HTML content of this segment",
        ),
    ]

    @field_validator("title", mode="before")
    @classmethod
    def force_unset_empty_title(cls, v: Any) -> str | None:
        return v if v else None


class ClientSegmentDocument(ClientSegment, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "segments"
        indexes = [
            "key",
            "locale",
        ]


ClientSegmentCreate = ClientSegment.create_model()
ClientSegmentRead = ClientSegment.read_model()
ClientSegmentUpdate = ClientSegment.update_model()


class ClientSegmentHead(BaseModel):
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
