import re

from beanie import PydanticObjectId
from pydantic import Field, validator
from textrig.models.common import Metadata, ModelBase


class LayerBase(ModelBase):
    """A data layer describing a set of data on a text"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this layer"
    )
    description: str = Field(
        None,
        min_length=1,
        max_length=128,
        description="Short, one-line description of this data layer",
    )
    text_id: PydanticObjectId | None = Field(
        None, description="ID of the text this layer belongs to"
    )
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(
        ..., description="A string identifying one of the available layer types"
    )
    # owner_id: DocId = Field(None)  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    class Settings:
        name = "layers"
        is_root = True

    @validator("description")
    def handle_whitespaces_in_description(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\s\n]+", " ", v)

    @validator("layer_type")
    def validate_layer_type_name(cls, v):
        from textrig.layer_types import get_layer_type_names

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


LayerBase._root_document_model = LayerBase.get_document_model()


# class LayerUpdateBase(LayerBase, metaclass=AllOptional):
#     """An update to an existing data layer"""

#     pass
