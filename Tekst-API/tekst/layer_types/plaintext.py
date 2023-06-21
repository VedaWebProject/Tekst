from pydantic import Field

from tekst.layer_types import LayerTypeABC
from tekst.models.common import LayerConfigBase
from tekst.models.layer import LayerBase
from tekst.models.layer_configs import DeepLLinksConfig
from tekst.models.unit import UnitBase


class PlainText(LayerTypeABC):
    """A simple plaintext layer type"""

    @classmethod
    def get_label(cls) -> str:
        return "PlainText"

    @classmethod
    def get_description(cls) -> str:
        return "A simple plaintext data layer"

    @classmethod
    def get_layer_model(cls) -> type["PlainTextLayer"]:
        return PlainTextLayer

    @classmethod
    def get_unit_model(cls) -> type["PlainTextUnit"]:
        return PlainTextUnit


class PlainTextLayerConfig(LayerConfigBase):
    deepl_links: DeepLLinksConfig = Field(default_factory=DeepLLinksConfig)


class PlainTextLayer(LayerBase):
    config: PlainTextLayerConfig = Field(default_factory=PlainTextLayerConfig)


class PlainTextUnit(UnitBase):
    """A unit of a plaintext data layer"""

    text: str | None = Field(
        None,
        description="Text content of the plaintext unit",
    )

    _template_fields = ("text",)
