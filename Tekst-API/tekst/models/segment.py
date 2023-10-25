from typing import Annotated

from pydantic import Field, model_validator

from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin


class ClientSegment(ModelBase, ModelFactoryMixin):
    key: Annotated[
        str,
        Field(
            description=(
                "Key of this segment. System segment keys must start with `system_`."
            ),
            max_length=32,
        ),
    ]
    is_system_segment: Annotated[
        bool,
        Field(
            description="Whether this is a system segment (will be set automatically)",
            alias="isSystemSegment",
        ),
    ] = False
    title: Annotated[
        str, Field(description="Title of this segment", max_length=32)
    ] = ""
    html: Annotated[
        str, Field(description="HTML content of this segment", max_length=1048576)
    ] = ""

    @model_validator(mode="after")
    def determine_if_system_segment(self) -> "ClientSegment":
        if self.key and self.key.startswith("system_"):
            self.is_system_segment = True
        return self


class ClientSegmentDocument(ClientSegment, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "segments"
        indexes = ["key", "is_system_segment"]


ClientSegmentCreate = ClientSegment.get_create_model()
ClientSegmentRead = ClientSegment.get_read_model()
ClientSegmentUpdate = ClientSegment.get_update_model()
