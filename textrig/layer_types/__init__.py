import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod

import pluggy
import pymongo
from textrig.logging import log
from textrig.models.common import TextRigBaseModel
from textrig.models.layer import LayerBase, LayerReadBase, LayerUpdateBase
from textrig.models.unit import UnitBase, UnitReadBase, UnitUpdateBase
from textrig.utils.strings import safe_name


# layer type plugin hook specification marker
_layer_type_spec = pluggy.HookspecMarker("textrig")

# layer type plugin hook implementation marker
layer_type_impl = pluggy.HookimplMarker("textrig")

# global variable to hold plugin manager instance
_layer_type_manager = None


class LayerTypePluginABC(ABC):
    """Abstract base class for defining a data layer type"""

    @classmethod
    @abstractmethod
    @_layer_type_spec
    def get_description(cls) -> str:
        """A short, one-line description of this layer type"""
        ...

    @classmethod
    @abstractmethod
    @_layer_type_spec
    def get_name(cls) -> str:
        """Returns the class name of this layer type plugin"""
        ...

    @classmethod
    def get_safe_name(cls) -> str:
        """Returns the slug of this layer type plugin's name"""
        return safe_name(cls.get_name(), max_len=16, delim="")

    @classmethod
    @abstractmethod
    @_layer_type_spec
    def get_layer_model(cls) -> type[LayerBase]:
        """Returns the layer base model for this type of data layer"""
        ...

    @classmethod
    @abstractmethod
    @_layer_type_spec
    def get_unit_model(cls) -> type[UnitBase]:
        """Returns the unit base model for units of this type of data layer"""
        ...

    @classmethod
    def get_common_index_models(cls) -> list[pymongo.IndexModel]:
        return [
            pymongo.IndexModel(
                [
                    ("layerId", pymongo.ASCENDING),
                ],
                name="layerId",
            ),
            pymongo.IndexModel(
                [
                    ("nodeId", pymongo.ASCENDING),
                ],
                name="nodeId",
            ),
        ]

    @classmethod
    @abstractmethod
    @_layer_type_spec
    def get_index_models(cls) -> list[pymongo.IndexModel]:
        """Returns the model for the database index of this layer type"""
        ...

    @classmethod
    def get_collection_name(cls) -> str:
        return f"units_{cls.get_safe_name()}"

    @classmethod
    def _get_model(cls, model_class_name: str, bases: tuple) -> type[TextRigBaseModel]:
        if not hasattr(cls, model_class_name):
            # model doesn't exist, has to be created
            model = type(
                model_class_name,
                bases,
                {"__module__": f"{cls.__module__}.{cls.__name__}"},
            )
            # and set as an attribute of the respective layer type class
            setattr(cls, model_class_name, model)
        # return model
        return getattr(cls, model_class_name)

    @classmethod
    def get_layer_read_model(cls) -> type[LayerReadBase]:
        """
        Dynamically generates and returns the layer read model
        for this type of data layer
        """
        layer_model = cls.get_layer_model()
        return cls._get_model(
            f"{layer_model.__name__}Read",
            (layer_model, LayerReadBase),
        )

    @classmethod
    def get_layer_update_model(cls) -> type[LayerUpdateBase]:
        """
        Dynamically generates and returns the layer update model
        for this type of data layer
        """
        layer_model = cls.get_layer_model()
        return cls._get_model(
            f"{layer_model.__name__}Update",
            (layer_model, LayerUpdateBase),
        )

    @classmethod
    def get_unit_read_model(cls) -> type[UnitReadBase]:
        """
        Dynamically generates and returns the unit read model
        for units of this type of data layer
        """
        unit_model = cls.get_unit_model()
        return cls._get_model(
            f"{unit_model.__name__}Read",
            (unit_model, UnitReadBase),
        )

    @classmethod
    def get_unit_update_model(cls) -> type[UnitUpdateBase]:
        """
        Dynamically generates and returns the unit update model
        for units of this type of data layer
        """
        unit_model = cls.get_unit_model()
        return cls._get_model(
            f"{unit_model.__name__}Update",
            (unit_model, UnitUpdateBase),
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


def get_layer_types() -> dict[str, LayerTypePluginABC]:
    """
    Returns a dict of all layer types, mapping from
    the layer type's safe name to a layer type plugin instance

    :return: A dict of all layer types
    :rtype: dict[str, LayerTypeABC]
    """
    return {p[0]: p[1] for p in _get_layer_type_manager().list_name_plugin()}


def get_layer_type_names() -> list[str]:
    """
    Returns a list of the names/slugs of all existing layer types

    :return: A list of all layer type names (lowercased slugs)
    :rtype: list[str]
    """
    return [p[0] for p in _get_layer_type_manager().list_name_plugin()]


def get_layer_type(layer_type_name: str) -> LayerTypePluginABC:
    """
    Returns a specific layer type plugin instance by name

    :param layer_type_name: Layer type safe name
    :type layer_type_name: str
    :return: The requested layer type plugin instance
    :rtype: LayerTypeABC
    """
    return _get_layer_type_manager().get_plugin(layer_type_name.lower())


def _get_layer_type_manager() -> pluggy.PluginManager:
    if _layer_type_manager is None:
        init_layer_type_manager()
    return _layer_type_manager


def init_layer_type_manager() -> None:
    global _layer_type_manager
    if _layer_type_manager is not None:
        return
    log.info("Initializing layer type plugin manager")
    # init manager
    manager = pluggy.PluginManager("textrig")
    # register layer type plugin specification
    manager.add_hookspecs(LayerTypePluginABC)
    # get internal layer type module names
    lt_modules = [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{__name__}.{lt_module.lower()}")
        plugins_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, LayerTypePluginABC)
        )
        # exclude LayerTypeABC class (which is weirdly picked up here)
        for sc in plugins_from_module:
            if sc[1] is not LayerTypePluginABC:
                plugin = sc[1]
                log.info(f"Registering internal layer type plugin: {plugin.get_name()}")
                manager.register(plugin(), plugin.get_safe_name())

    # load and register plugins that might be available from external packages
    manager.load_setuptools_entrypoints(group="textrig")
    # set global reference
    _layer_type_manager = manager
