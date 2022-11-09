import abc
import importlib

from pydantic import Field
from textrig.models.common import Metadata, PyObjectId, TextRigBaseModel


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
