from typing import Literal

from pydantic import Field

from tekst.models.common import ResourceConfigBase
from tekst.models.resource import ResourceBase
from tekst.models.unit import UnitBase
from tekst.resource_types import ResourceTypeABC


class Debug(ResourceTypeABC):
    """A simple plaintext resource type"""

    @classmethod
    def get_description(cls) -> str:
        return "Just a temporary debug resource"

    @classmethod
    def resource_model(cls) -> type["DebugResource"]:
        return DebugResource

    @classmethod
    def unit_model(cls) -> type["DebugUnit"]:
        return DebugUnit


class DebugResourceConfig(ResourceConfigBase):
    pass


class DebugResource(ResourceBase):
    resource_type: Literal["debug"]  # snake_cased resource type classname
    config: DebugResourceConfig = DebugResourceConfig()


class DebugUnit(UnitBase):
    """A unit of a plaintext resource"""

    resource_type: Literal["debug"]  # snake_cased resource type classname
    text: str | None = Field(
        None,
        description="Text content of the debug unit",
    )

    _template_fields = ("text",)