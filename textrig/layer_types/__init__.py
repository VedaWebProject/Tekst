import abc
import importlib
import pkgutil
import types

from textrig import layer_types
from textrig.models.layer import UnitBase


class LayerTypeABC(abc.ABC):
    """Abstract base class for defining a data layer type"""

    @staticmethod
    @abc.abstractmethod
    def get_unit_models() -> dict[type[UnitBase]]:
        ...

    @staticmethod
    @abc.abstractmethod
    def get_unit_template() -> dict:
        ...

    unit_models: dict[type[UnitBase]] = property(fget=get_unit_models)
    unit_template: dict = property(fget=get_unit_template)


def get_layer_type_module(layer_type_name: str) -> types.ModuleType:
    return importlib.import_module(f"textrig.layer_types.{layer_type_name.lower()}")


def get_layer_type_names() -> list[str]:
    return [mod.name for mod in pkgutil.iter_modules(layer_types.__path__)]


def get_layer_type(layer_type_name: str) -> type[LayerTypeABC]:
    return get_layer_type_module(layer_type_name).Unit
