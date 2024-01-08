from typing import Annotated, Literal

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, StringConstraints, model_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    TranslationLocaleKey,
)


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
    is_system_segment: Annotated[
        bool,
        Field(
            description="Whether this is a system segment (will be set automatically)",
            alias="isSystemSegment",
        ),
    ] = False
    editor_mode: Annotated[
        Literal["wysiwyg", "html"], Field(description="Last used editor mode")
    ] = "wysiwyg"
    locale: Annotated[
        TranslationLocaleKey,
        Field(description="Locale indicating the translation language of this segment"),
    ]
    title: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=32, strip_whitespace=True),
        Field(description="Title of this segment"),
    ] = None
    html: Annotated[
        str,
        StringConstraints(min_length=1, max_length=1048576, strip_whitespace=True),
        Field(description="HTML content of this segment"),
    ]

    @model_validator(mode="after")
    def set_is_system_segment(self) -> "ClientSegment":
        if self.key and self.key.startswith("system"):
            self.is_system_segment = True
        return self


class ClientSegmentDocument(ClientSegment, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "segments"
        indexes = ["key", "is_system_segment", "locale"]


ClientSegmentCreate = ClientSegment.create_model()
ClientSegmentRead = ClientSegment.read_model()
ClientSegmentUpdate = ClientSegment.update_model()


class ClientSegmentHead(BaseModel):
    id: PydanticObjectId
    key: str
    title: str | None = None
    locale: TranslationLocaleKey

    class Settings:
        projection = {"id": "$_id", "key": 1, "title": 1, "locale": 1}
