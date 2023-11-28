import importlib
import inspect
import pkgutil

from abc import ABC, abstractmethod
from typing import Annotated, Union

from fastapi import Body
from humps import decamelize

from tekst.logging import log
from tekst.models.common import ReadBase
from tekst.models.layer import (
    LayerBase,
    LayerBaseDocument,
    LayerBaseUpdate,
    LayerReadExtras,
)
from tekst.models.unit import UnitBase, UnitBaseDocument, UnitBaseUpdate


class LayerTypeABC(ABC):
    """Abstract base class for defining a data layer type"""

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """A short, one-line description of this layer type"""
        ...

    @classmethod
    def get_name(cls) -> str:
        """Returns the name of this layer type"""
        return cls.__name__

    @classmethod
    def get_key(cls) -> str:
        """Returns the key identifying this layer type"""
        return decamelize(cls.__name__)

    @classmethod
    @abstractmethod
    def layer_model(cls) -> type[LayerBase]:
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
        create_model = cls.get_unit_model().create_model()
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


class LayerTypeManager:
    __layer_types: dict[str, LayerTypeABC] = dict()

    def register(self, layer_type_class: type[LayerTypeABC], layer_type_name: str):
        # create layer/unit document models
        layer_type_class.layer_model().document_model(LayerBaseDocument)
        layer_type_class.layer_model().update_model(LayerBaseUpdate)
        layer_type_class.get_unit_model().document_model(UnitBaseDocument)
        layer_type_class.get_unit_model().update_model(UnitBaseUpdate)
        # register instance
        self.__layer_types[layer_type_name.lower()] = layer_type_class()

    def get(self, layer_type_name: str) -> LayerTypeABC:
        return self.__layer_types.get(layer_type_name.lower())

    def get_all(self) -> dict[str, LayerTypeABC]:
        return self.__layer_types

    def list_names(self) -> list[str]:
        return list(self.__layer_types.keys())


def init_layer_types_mgr() -> None:
    global layer_types_mgr
    if layer_types_mgr is not None:
        return layer_types_mgr
    log.info("Initializing layer types...")
    # init manager
    manager = LayerTypeManager()
    # get internal layer type module names
    lt_modules = [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{__name__}.{lt_module.lower()}")
        layer_types_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, LayerTypeABC)
        )
        for layer_type_impl in layer_types_from_module:
            # exclude LayerTypeABC class (which is weirdly picked up here)
            if layer_type_impl[1] is not LayerTypeABC:
                layer_type_class = layer_type_impl[1]
                # initialize layer type CRUD models (don't init document models here!)
                layer_type_class.layer_model().create_model()
                layer_type_class.layer_model().read_model((LayerReadExtras, ReadBase))
                layer_type_class.layer_model().update_model()
                # register layer type instance with layer type manager
                log.info(f"Registering layer type: {layer_type_class.get_name()}")
                manager.register(layer_type_class, layer_type_class.get_key())
    layer_types_mgr = manager


# global variable to hold layer type manager instance
layer_types_mgr: LayerTypeManager = None
init_layer_types_mgr()


# ### create union type aliases for models of any layer type model

# CREATE
AnyLayerCreate = Union[  # noqa: UP007
    tuple(
        [lt.layer_model().create_model() for lt in layer_types_mgr.get_all().values()]
    )
]
AnyLayerCreateBody = Annotated[
    AnyLayerCreate,
    Body(discriminator="layer_type"),
]

# READ
AnyLayerRead = Union[  # noqa: UP007
    tuple([lt.layer_model().read_model() for lt in layer_types_mgr.get_all().values()])
]
AnyLayerReadBody = Annotated[
    AnyLayerRead,
    Body(discriminator="layer_type"),
]

# UPDATE
AnyLayerUpdate = Union[  # noqa: UP007
    tuple(
        [lt.layer_model().update_model() for lt in layer_types_mgr.get_all().values()]
    )
]
AnyLayerUpdateBody = Annotated[
    AnyLayerUpdate,
    Body(discriminator="layer_type"),
]

# DOCUMENT
AnyLayerDocument = Union[  # noqa: UP007
    tuple(
        [lt.layer_model().document_model() for lt in layer_types_mgr.get_all().values()]
    )
]
