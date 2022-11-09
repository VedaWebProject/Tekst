import abc
import importlib

from pydantic import Field
from textrig.models.common import Metadata, PyObjectId, TextRigBaseModel


class UnitBase(TextRigBaseModel, abc.ABC):
    """A type of data unit belonging to a certain data layer"""

    layer_id: PyObjectId = Field(..., description="Parent data layer ID")
    node_id: PyObjectId = Field(..., description="Parent text node ID")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    @staticmethod
    @abc.abstractmethod
    def get_template() -> dict:
        """
        Returns a dict defining the import template layout for this unit type

        Fields that are to be filled in the template should have a value of None
        instead of an "empty" literal like ""

        :return: dict containing the template
        :rtype: dict
        """

        ...


def get_unit_type(type_name: str) -> type[UnitBase]:
    """
    Loads a specific data layer unit type by its type name during runtime

    :param type_name: Name of the unit type to load (will be lower-cased)
    :type type_name: str
    :return: The class of the requested unit type
    :rtype: type[UnitBase]
    """

    return importlib.import_module(f"textrig.models.units.{type_name.lower()}").Unit
