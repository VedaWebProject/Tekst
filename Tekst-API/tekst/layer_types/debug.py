from typing import Literal

from pydantic import Field

from tekst.layer_types import LayerTypeABC
from tekst.models.common import LayerConfigBase
from tekst.models.layer import LayerBase
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
    def unit_model(cls) -> type["DebugUnit"]:
        return DebugUnit


class DebugLayerConfig(LayerConfigBase):
    pass


class DebugLayer(LayerBase):
    layer_type: Literal["debug"]  # snake_cased layer type classname
    config: DebugLayerConfig = DebugLayerConfig()


class DebugUnit(UnitBase):
    """A unit of a plaintext data layer"""

    layer_type: Literal["debug"]  # snake_cased layer type classname
    text: str | None = Field(
        None,
        description="Text content of the debug unit",
    )

    _template_fields = ("text",)
