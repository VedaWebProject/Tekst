import importlib
import inspect
import pkgutil

from abc import ABC, abstractmethod

from tekst.logging import log
from tekst.models.common import ModelBase
from tekst.models.layer import LayerBase, LayerBaseDocument, LayerBaseUpdate
from tekst.models.unit import UnitBase, UnitBaseDocument, UnitBaseUpdate
from tekst.utils.strings import safe_name


class LayerTypeABC(ABC):
    """Abstract base class for defining a data layer type"""

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """A short, one-line description of this layer type"""
        ...

    @classmethod
    @abstractmethod
    def get_label(cls) -> str:
        """Returns the class name of this layer type"""
        ...

    @classmethod
    def get_name(cls) -> str:
        """Returns the slug of this layer type's name"""
        return safe_name(cls.get_label(), max_len=16, delim="")

    @classmethod
    @abstractmethod
    def get_layer_model(cls) -> type[LayerBase]:
        """Returns the layer base model for this type of data layer"""
        ...

    @classmethod
    @abstractmethod
    def get_unit_model(cls) -> type[UnitBase]:
        """Returns the unit base model for units of this type of data layer"""
        ...

    @classmethod
    def prepare_import_template(cls) -> dict:
        """Returns the base template for import data for this data layer type"""
        create_model = cls.get_unit_model().get_create_model()
        schema = create_model.schema()
        template_fields = create_model.get_template_fields()
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
            if prop in template_fields:
                unit_schema = {k: v for k, v in val.items() if k in include_layer_props}
                unit_schema["required"] = prop in required
                template["_unitSchema"][prop] = unit_schema
        return template


class LayerTypeInfo(ModelBase):
    name: str
    label: str
    description: str


class LayerTypeManager:
    __layer_types: dict[str, LayerTypeABC] = dict()

    def register(self, layer_type_class: type[LayerTypeABC], layer_type_name: str):
        # create layer/unit document models
        layer_type_class.get_layer_model().get_document_model(LayerBaseDocument)
        layer_type_class.get_layer_model().get_update_model(LayerBaseUpdate)
        layer_type_class.get_unit_model().get_document_model(UnitBaseDocument)
        layer_type_class.get_unit_model().get_update_model(UnitBaseUpdate)
        # register instance
        self.__layer_types[layer_type_name.lower()] = layer_type_class()

    def get(self, layer_type_name: str) -> LayerTypeABC:
        return self.__layer_types.get(layer_type_name.lower())

    def get_all(self) -> dict[str, LayerTypeABC]:
        return self.__layer_types

    def list_names(self) -> list[str]:
        return list(self.__layer_types.keys())

    def get_layer_types_info(self) -> list[LayerTypeInfo]:
        """Returns a list of all available data layer types"""
        return sorted(
            [
                {
                    "name": lt.get_name(),
                    "label": lt.get_label(),
                    "description": lt.get_description(),
                }
                for lt in self.__layer_types.values()
            ],
            key=lambda lt: lt["name"],
        )


def init_layer_type_manager() -> None:
    global layer_type_manager
    if layer_type_manager is not None:
        return layer_type_manager
    log.info("Initializing layer type manager")
    # init manager
    manager = LayerTypeManager()
    # get internal layer type module names
    lt_modules = [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{__name__}.{lt_module.lower()}")
        layer_types_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, LayerTypeABC)
        )
        # exclude LayerTypeABC class (which is weirdly picked up here)
        for layer_type_impl in layer_types_from_module:
            if layer_type_impl[1] is not LayerTypeABC:
                layer_type_class = layer_type_impl[1]
                # register layer type instance with layer type manager
                log.info(f"Registering layer type: {layer_type_class.get_name()}")
                manager.register(layer_type_class, layer_type_class.get_name())
    layer_type_manager = manager


# global variable to hold layer type manager instance
layer_type_manager: LayerTypeManager = None
init_layer_type_manager()
