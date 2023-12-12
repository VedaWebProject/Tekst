from typing import Literal

from pydantic import Field

from tekst.layer_types import LayerTypeABC
from tekst.models.common import LayerConfigBase
from tekst.models.layer import LayerBase
from tekst.models.layer_configs import DeepLLinksConfig
from tekst.models.unit import UnitBase


class Plaintext(LayerTypeABC):
    """A simple plaintext layer type"""

    @classmethod
    def get_description(cls) -> str:
        return "A simple plaintext data layer"

    @classmethod
    def layer_model(cls) -> type["PlaintextLayer"]:
        return PlaintextLayer

    @classmethod
    def unit_model(cls) -> type["PlaintextUnit"]:
        return PlaintextUnit


class PlaintextLayerConfig(LayerConfigBase):
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlaintextLayer(LayerBase):
    layer_type: Literal["plaintext"]  # snake_cased layer type classname
    config: PlaintextLayerConfig = PlaintextLayerConfig()


class PlaintextUnit(UnitBase):
    """A unit of a plaintext data layer"""

    layer_type: Literal["plaintext"]  # snake_cased layer type classname
    text: str | None = Field(
        None,
        description="Text content of the plaintext unit",
    )

    _template_fields = ("text",)
