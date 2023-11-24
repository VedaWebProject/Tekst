from typing import Literal

from pydantic import Field

from tekst.layer_types import LayerTypeABC
from tekst.models.common import LayerConfigBase
from tekst.models.layer import LayerBase
from tekst.models.layer_configs import DeepLLinksConfig
from tekst.models.unit import UnitBase


class Debug(LayerTypeABC):
    """A simple plaintext layer type"""

    @classmethod
    def get_description(cls) -> str:
        return "Just a temporary debug layer"

    @classmethod
    def layer_model(cls) -> type["DebugLayer"]:
        return DebugLayer

    @classmethod
    def get_unit_model(cls) -> type["DebugUnit"]:
        return DebugUnit


class DebugLayerConfig(LayerConfigBase):
    deepl_links: DeepLLinksConfig = Field(default_factory=DeepLLinksConfig)


class DebugLayer(LayerBase):
    layer_type: Literal["debug"]  # snake_cased layer type classname
    config: DebugLayerConfig = Field(default_factory=DebugLayerConfig)


class DebugUnit(UnitBase):
    """A unit of a plaintext data layer"""

    text: str | None = Field(
        None,
        description="Text content of the debug unit",
    )

    _template_fields = ("text",)
