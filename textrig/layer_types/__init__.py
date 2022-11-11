import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from types import ModuleType

from pydantic import Field
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)


class LayerTypeABC(ABC):
    """Abstract base class for defining a data layer type"""

    class UnitBase(ABC, TextRigBaseModel):
        """A base class for types of data units belonging to a certain data layer"""

        layer_id: DocumentId = Field(..., description="Data layer ID")
        node_id: DocumentId = Field(..., description="Parent text node ID")
        meta: Metadata = Field(
            None,
            description="Arbitrary metadata on this layer unit",
            extra={"template": True},
        )

    class UnitReadBase(UnitBase, DbDocument):
        ...

    class UnitUpdateBase(UnitBase, metaclass=AllOptional):
        ...

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        return (
            "A TextRig data layer "
            "(this generic description has apparently not been properly overridden)"
        )

    @classmethod
    @abstractmethod
    def get_unit_model(cls) -> type[UnitBase]:
        """Returns the unit base model for units of this type of data layer"""
        raise NotImplementedError(f"This method should have been implemented in {cls}")

    @classmethod
    @abstractmethod
    def get_unit_read_model(cls) -> type[UnitReadBase]:
        """
        Dynamically generates and returns the unit read model
        for units of this type of data layer
        """
        return type(
            f"{cls.get_unit_model().__name__}Read",
            (cls.get_unit_model(), cls.UnitReadBase),
            {},
        )

    @classmethod
    @abstractmethod
    def get_unit_update_model(cls) -> type[UnitUpdateBase]:
        """
        Dynamically generates and returns the unit update model
        for units of this type of data layer
        """
        return type(
            f"{cls.get_unit_model().__name__}Update",
            (cls.get_unit_model(), cls.UnitUpdateBase),
            {},
        )

    @classmethod
    def prepare_import_template(cls) -> dict:
        """Returns the base template for import data for this data layer type"""
        schema = cls.get_unit_model().schema()
        required = schema.get("required", [])
        include_layer_props = ("description", "type", "additionalProperties")
        template = {
            "_title": "Title of this data layer",  # will be overridden
            "_level": -1,  # will be overridden
            "_description": cls.get_description(),
            "_unitSchema": {},  # will be populated in the next step
            "units": [],  # will be populated on template request
        }
        # generate unit schema for the template
        for prop, val in schema.get("properties", {}).items():
            if val.get("extra") and val.get("extra").get("template"):
                unit_schema = {k: v for k, v in val.items() if k in include_layer_props}
                unit_schema["required"] = prop in required
                template["_unitSchema"][prop] = unit_schema
        return template


# global variable to store a dict of all existing layer types
_layer_types: dict[str, LayerTypeABC] = None


def get_layer_types() -> dict[str, type[LayerTypeABC]]:
    """
    Returns a dict of all layer types, mapping from
    the layer type's slug to the layer type's class

    :return: A dict of all layer types
    :rtype: dict[str, type[LayerTypeABC]]
    """
    global _layer_types
    if _layer_types:
        return _layer_types
    _layer_types = {}
    for ltype_name in get_layer_type_names():
        module = _get_layer_type_module(ltype_name)
        subclasses_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, LayerTypeABC)
        )
        for sc in subclasses_from_module:
            if sc[1] is not LayerTypeABC:
                _layer_types[ltype_name] = sc[1]
    return _layer_types


def _get_layer_type_module(layer_type_name: str) -> ModuleType:
    """
    Returns a specific layer type module by name

    :param layer_type_name: Layer type module name
    :type layer_type_name: str
    :return: The requested module
    :rtype: ModuleType
    """
    return importlib.import_module(f"{__name__}.{layer_type_name.lower()}")


def get_layer_type_names() -> list[str]:
    """
    Returns a list of the names/slugs of all existing layer types

    :return: A list of all layer type names (lowercased slugs)
    :rtype: list[str]
    """
    return [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]


def get_layer_type(layer_type_name: str) -> type[LayerTypeABC]:
    """
    Returns a specific layer type's class by name

    :param layer_type_name: Layer type name/slug
    :type layer_type_name: str
    :return: The requested layer type's class
    :rtype: type[LayerTypeABC]
    """
    return get_layer_types().get(layer_type_name, None)
