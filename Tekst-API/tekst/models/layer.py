import re

from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, In, Or
from pydantic import ConfigDict, Field, field_validator, model_validator

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead


class LayerBase(ModelBase, ModelFactoryMixin):
    """A data layer describing a set of data on a text"""

    title: Annotated[
        str, Field(min_length=1, max_length=64, description="Title of this layer")
    ]
    description: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=512,
            description="Short, concise description of this data layer",
        ),
    ] = None
    text_id: Annotated[
        PydanticObjectId | None,
        Field(description="ID of the text this layer belongs to"),
    ] = None
    level: Annotated[int, Field(description="Text level this layer belongs to")]
    layer_type: Annotated[
        str, Field(description="A string identifying one of the available layer types")
    ]
    owner_id: Annotated[
        PydanticObjectId | None, Field(description="User owning this layer")
    ] = None
    shared_read: Annotated[
        list[PydanticObjectId] | None,
        Field(description="Users with shared read access to this layer"),
    ] = None
    shared_write: Annotated[
        list[PydanticObjectId] | None,
        Field(description="Users with shared write access to this layer"),
    ] = None
    public: Annotated[
        bool, Field(description="Publication status of this layer")
    ] = False
    proposed: Annotated[
        bool, Field(description="Whether this layer has been proposed for publication")
    ] = False
    citation: Annotated[
        str | None,
        Field(description="Citation details for this layer", max_length=1000),
    ] = None
    meta: Annotated[Metadata | None, Field(description="Arbitrary metadata")] = None
    comment: Annotated[
        str | None,
        Field(description="Plaintext, potentially multiline comment on this layer"),
    ] = None

    @field_validator("description")
    @classmethod
    def handle_whitespaces_in_description(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\s\n\r]+", " ", v)

    @field_validator("layer_type")
    @classmethod
    def validate_layer_type_name(cls, v):
        from tekst.layer_types import layer_type_manager

        layer_type_names = layer_type_manager.list_names()
        if v.lower() not in layer_type_names:
            raise ValueError(
                f"Given layer type ({v}) is not a valid "
                f"layer type name (one of {layer_type_names})."
            )
        return v.lower()

    @model_validator(mode="after")
    def model_postprocess(self):
        # cannot be both public and proposed, public has priority
        if self.public:
            self.proposed = False
        return self

    def restricted_fields(self, user_id: str = None) -> dict:
        return {
            "shared_read": user_id is None or self.owner_id != user_id,
            "shared_write": user_id is None or self.owner_id != user_id,
        }


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class LayerBaseDocument(LayerBase, DocumentBase):
    @classmethod
    async def allowed_to_read(cls, user: UserRead | None) -> dict:
        if not user:
            return {"public": True}
        if user.is_superuser:
            return {}

        active_texts_ids = [
            text.id
            for text in await TextDocument.find(
                TextDocument.is_active == True  # noqa: E712
            ).to_list()
        ]

        return And(
            Or(In(LayerBaseDocument.text_id, active_texts_ids), {"owner_id": user.id}),
            Or(
                {"public": True},
                {"proposed": True},
                {"owner_id": user.id},
                {"shared_read": user.id},
                {"shared_write": user.id},
            ),
        )

    @classmethod
    def allowed_to_write(cls, user: UserRead | None) -> dict:
        if user.is_superuser:
            return {}
        uid = user.id if user else "no_id"
        return Or(
            {"owner_id": uid},
            {"shared_write": uid},
        )

    class Settings(DocumentBase.Settings):
        name = "layers"
        is_root = True
        indexes = ["text_id", "level", "layer_type", "owner_id"]


LayerBaseRead = LayerBase.get_read_model()
LayerBaseUpdate = LayerBase.get_update_model()


class AnyLayerRead(LayerBaseRead):
    model_config = ConfigDict(extra="allow")

    def include_writable(self, user: UserRead | None):
        if not user:
            return
        self.writable = (
            user.is_superuser
            or user.id == self.owner_id
            or user.id in self.shared_write
        )


class LayerNodeCoverage(ModelBase):
    label: str
    position: int
    covered: bool
