import abc
import importlib

from pydantic import Field
from textrig.models.common import (
    AllOptional,
    Metadata,
    ObjectInDB,
    PyObjectId,
    TextRigBaseModel,
)


# === (TEXT) LAYER ===


class Layer(TextRigBaseModel):
    """A data layer describing a set of data on a text"""

    text_slug: str = Field(..., description="Slug of the text this layer belongs to")
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(...)
    # owner_id: PyObjectId = Field(None)  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata | None = Field(None, description="Arbitrary metadata")


class LayerRead(Layer, ObjectInDB):

    ...


class LayerUpdate(Layer, metaclass=AllOptional):

    ...


# === (LAYER) UNIT TYPE BASE CLASS ===


class UnitTypeBase(TextRigBaseModel, abc.ABC):
    """A unit of data belonging to a certain data layer"""

    layer_id: PyObjectId = Field(..., description="Parent data layer ID")
    node_id: PyObjectId = Field(..., description="Parent text node ID")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    @staticmethod
    @abc.abstractmethod
    def get_template() -> dict:
        ...


def get_unit_type(type_name: str) -> UnitTypeBase:
    return importlib.import_module(f"textrig.models.unit_types.{type_name}").UnitType
