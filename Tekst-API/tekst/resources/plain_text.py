from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import DeepLLinksConfig, ResourceConfigBase
from tekst.resources import ResourceTypeABC


class PlainText(ResourceTypeABC):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: Annotated[
        bool,
        Field(
            description=(
                "Whether contents of this resource should be collapsed by default"
            )
        ),
    ] = False
    reduced_view_oneline: Annotated[
        bool,
        Field(description="Show contents as single line of text when in reduced view"),
    ] = False


class PlainTextResourceConfig(ResourceConfigBase):
    general: GeneralPlainTextResourceConfig = GeneralPlainTextResourceConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlainTextResource(ResourceBase):
    resource_type: Literal["plainText"]  # camelCased resource type classname
    config: PlainTextResourceConfig = PlainTextResourceConfig()


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400, strip_whitespace=True),
        Field(
            description="Text content of the plain text content object",
        ),
    ]
