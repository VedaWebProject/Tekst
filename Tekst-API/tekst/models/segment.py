from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

from tekst.models.common import DocumentBase, Locale, ModelBase, ModelFactoryMixin


class ClientSegment(ModelBase, ModelFactoryMixin):
    key: Annotated[
        str,
        Field(
            description=(
                "Key of this segment. System segment keys must start with `system_`."
            ),
        ),
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=32,
            pattern=r"[a-zA-Z0-9\-_]+",
        ),
    ]
    is_system_segment: Annotated[
        bool,
        Field(
            description="Whether this is a system segment (will be set automatically)",
            alias="isSystemSegment",
        ),
    ] = False
    locale: Annotated[
        Locale | Literal["*"],
        Field(description="Locale indicating the translation language of this segment"),
    ]
    title: Annotated[
        str | None, Field(description="Title of this segment", max_length=32)
    ] = None
    html: Annotated[
        str, Field(description="HTML content of this segment", max_length=1048576)
    ]

    @model_validator(mode="after")
    def set_is_system_segment(self) -> "ClientSegment":
        if self.key and self.key.startswith("system_"):
            self.is_system_segment = True
        return self


class ClientSegmentDocument(ClientSegment, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "segments"
        indexes = ["key", "is_system_segment", "locale"]


ClientSegmentCreate = ClientSegment.get_create_model()
ClientSegmentRead = ClientSegment.get_read_model()
ClientSegmentUpdate = ClientSegment.get_update_model()


class ClientSegmentHead(BaseModel):
    key: str
    title: str
    locale: Locale
