from pydantic import Field
from textrig.models.common import (
    AllOptional,
    BaseModel,
    Metadata,
    ObjectInDB,
    PyObjectId,
)


# === (TEXT) LAYER ===


class Layer(BaseModel):
    """A data layer describing a set of data on a text"""

    text_slug: str = Field(..., description="Slug of the text this layer belongs to")
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(...)
    owner_id: PyObjectId = Field(PyObjectId())  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata | None = Field(None, description="Arbitrary metadata")


class LayerRead(Layer, ObjectInDB):

    ...


class LayerUpdate(Layer, metaclass=AllOptional):

    ...


# === (LAYER) UNIT BASE CLASS ===


class Unit(BaseModel):
    """A unit of data belonging to a certain data layer"""

    layer_id: PyObjectId = Field(..., description="Parent data layer ID")
    node_id: PyObjectId = Field(..., description="Parent text node ID")
    meta: Metadata | None = Field(None, description="Arbitrary metadata")
