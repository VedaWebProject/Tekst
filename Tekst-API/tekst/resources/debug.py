from typing import Literal

from pydantic import Field

from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import ResourceConfigBase
from tekst.resources import ResourceTypeABC


class Debug(ResourceTypeABC):  # pragma: no cover
    """A simple plaintext resource type"""

    @classmethod
    def resource_model(cls) -> type["DebugResource"]:
        return DebugResource

    @classmethod
    def content_model(cls) -> type["DebugContent"]:
        return DebugContent


class DebugResourceConfig(ResourceConfigBase):
    pass


class DebugResource(ResourceBase):
    resource_type: Literal["debug"]  # snake_cased resource type classname
    config: DebugResourceConfig = DebugResourceConfig()


class DebugContent(ContentBase):
    """A content of a plaintext resource"""

    resource_type: Literal["debug"]  # snake_cased resource type classname
    text: str | None = Field(
        None,
        description="Text content of the debug content",
    )
