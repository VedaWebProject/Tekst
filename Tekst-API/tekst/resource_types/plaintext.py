from typing import Literal

from pydantic import Field

from tekst.models.common import ResourceConfigBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import DeepLLinksConfig
from tekst.models.unit import UnitBase
from tekst.resource_types import ResourceTypeABC


class Plaintext(ResourceTypeABC):
    """A simple plaintext resource type"""

    @classmethod
    def resource_model(cls) -> type["PlaintextResource"]:
        return PlaintextResource

    @classmethod
    def unit_model(cls) -> type["PlaintextUnit"]:
        return PlaintextUnit

    @classmethod
    def template_fields(cls) -> set[str]:
        return {"text"}


class PlaintextResourceConfig(ResourceConfigBase):
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlaintextResource(ResourceBase):
    resource_type: Literal["plaintext"]  # snake_cased resource type classname
    config: PlaintextResourceConfig = PlaintextResourceConfig()


class PlaintextUnit(UnitBase):
    """A unit of a plaintext resource"""

    resource_type: Literal["plaintext"]  # snake_cased resource type classname
    text: str | None = Field(
        None,
        description="Text content of the plaintext unit",
    )
