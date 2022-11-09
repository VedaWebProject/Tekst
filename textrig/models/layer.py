from pydantic import Field
from textrig.models.common import AllOptional, Metadata, ObjectInDB, TextRigBaseModel


class Layer(TextRigBaseModel):
    """A data layer describing a set of data on a text"""

    text_slug: str = Field(..., description="Slug of the text this layer belongs to")
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(...)
    # owner_id: PyObjectId = Field(None)  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata | None = Field(None, description="Arbitrary metadata")


class LayerRead(Layer, ObjectInDB):
    """An existing data layer read from the database"""
    ...


class LayerUpdate(Layer, metaclass=AllOptional):
    """An update to an existing data layer"""

    ...
