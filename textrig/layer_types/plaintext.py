from pydantic import Field

from textrig.layer_types import LayerTypePluginABC, layer_type_impl
from textrig.models.common import LayerConfigBase
from textrig.models.layer import LayerBase
from textrig.models.layer_configs import DeepLLinksConfig
from textrig.models.unit import UnitBase


class PlainText(LayerTypePluginABC):
    """A simple plaintext layer type"""

    @classmethod
    @layer_type_impl
    def get_name(cls) -> str:
        return "PlainText"

    @classmethod
    @layer_type_impl
    def get_description(cls) -> str:
        return "A simple plaintext data layer"

    @classmethod
    @layer_type_impl
    def get_layer_model(cls) -> type["PlainTextLayer"]:
        return PlainTextLayer

    @classmethod
    @layer_type_impl
    def get_unit_model(cls) -> type["PlainTextUnit"]:
        return PlainTextUnit


class PlainTextLayerConfig(LayerConfigBase):
    deepl_links: DeepLLinksConfig = Field(default_factory=DeepLLinksConfig)


class PlainTextLayer(LayerBase):
    config: PlainTextLayerConfig = Field(default_factory=PlainTextLayerConfig)

    @classmethod
    def get_layer_type_plugin_class(cls) -> type[PlainText]:
        return PlainText


class PlainTextUnit(UnitBase):
    """A unit of a plaintext data layer"""

    text: str | None = Field(
        None,
        description="Text content of the plaintext unit",
    )

    _template_fields = ("text",)

    @classmethod
    def get_layer_type_plugin_class(cls) -> type[PlainText]:
        return PlainText
