import re

from beanie.operators import Or
from pydantic import Field, validator

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactory,
    PyObjectId,
    ReadBase,
    UpdateBase,
)
from tekst.models.user import UserRead


class LayerBase(ModelBase, ModelFactory):
    """A data layer describing a set of data on a text"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this layer"
    )
    description: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        description="Short, one-line description of this data layer",
    )
    text_id: PyObjectId | None = Field(
        None, description="ID of the text this layer belongs to"
    )
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(
        ..., description="A string identifying one of the available layer types"
    )
    owner_id: PyObjectId | None = Field(None, description="User owning this layer")
    shared_read: list[PyObjectId] = Field(
        default_factory=list, description="Users with shared read access to this layer"
    )
    shared_write: list[PyObjectId] = Field(
        default_factory=list, description="Users with shared write access to this layer"
    )
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata | None = Field(None, description="Arbitrary metadata")
    comment: str | None = Field(
        None, description="Plaintext, potentially multiline comment on this layer"
    )

    @validator("description")
    def handle_whitespaces_in_description(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\s\n]+", " ", v)

    @validator("layer_type")
    def validate_layer_type_name(cls, v):
        from tekst.layer_types import get_layer_type_names

        layer_type_names = get_layer_type_names()
        if v.lower() not in layer_type_names:
            raise ValueError(
                f"Given layer type ({v}) is not a valid "
                f"layer type name (one of {layer_type_names})."
            )
        return v.lower()

    @classmethod
    def get_layer_type_plugin_class(cls) -> type:
        raise NotImplementedError(
            "Method LayerBase.get_layer_type_plugin_class must be overridden!"
        )


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class LayerBaseDocument(LayerBase, DocumentBase):
    @classmethod
    def allowed_to_read(cls, user: UserRead | None) -> dict:
        uid = user.id if user else "no_id"
        if not user:
            return {"public": True}
        if user.is_superuser:
            return {}
        return Or(
            {"public": True},
            {"ownerId": uid},
            {"sharedRead": uid},
            {"sharedWrite": uid},
        )

    @classmethod
    def allowed_to_write(cls, user: UserRead | None) -> dict:
        uid = user.id if user else "no_id"
        if not user:
            return {"public": True}
        if user.is_superuser:
            return {}
        return Or(
            {"ownerId": uid},
            {"sharedWrite": uid},
        )

    def restricted_fields(self, user_id: str = None) -> dict:
        return {
            "shared_read": user_id is None or self.owner_id != user_id,
            "shared_write": user_id is None or self.owner_id != user_id,
        }

    class Settings(DocumentBase.Settings):
        name = "layers"
        is_root = True
        indexes = ["textId", "level", "layerType", "ownerId"]


class LayerBaseRead(LayerBase, ReadBase):
    pass


class LayerBaseUpdate(LayerBase, UpdateBase):
    pass


class LayerMinimalView(ReadBase):
    layer_type: str
