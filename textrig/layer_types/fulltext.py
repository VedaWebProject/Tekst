import pymongo
from pydantic import Field
from textrig.layer_types import LayerTypePluginABC, layer_type_impl
from textrig.models.layer import LayerBase
from textrig.models.unit import UnitBase


class FulltextLayer(LayerBase):
    @classmethod
    def get_layer_type_plugin_class(cls) -> type["Fulltext"]:
        return Fulltext


class FulltextUnit(UnitBase):
    """A unit of a fulltext data layer"""

    text: str = Field(
        None,
        description="Text content of the fulltext unit",
        extra={"template": True},
    )

    @classmethod
    def get_layer_type_plugin_class(cls) -> type["Fulltext"]:
        return Fulltext


class Fulltext(LayerTypePluginABC):
    """A simple fulltext layer type"""

    @classmethod
    @layer_type_impl
    def get_name(cls) -> str:
        return "Fulltext"

    @classmethod
    @layer_type_impl
    def get_description(cls) -> str:
        return "A simple fulltext data layer"

    @classmethod
    @layer_type_impl
    def get_layer_model(cls) -> type[FulltextLayer]:
        return FulltextLayer

    @classmethod
    @layer_type_impl
    def get_unit_model(cls) -> type[FulltextUnit]:
        return FulltextUnit

    @classmethod
    @layer_type_impl
    def get_index_models(cls) -> list[pymongo.IndexModel]:
        return [pymongo.IndexModel([("text", pymongo.TEXT)], name="text", unique=False)]
