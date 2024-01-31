from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import ResourceConfigBase
from tekst.resources import ResourceTypeABC


class RichText(ResourceTypeABC):
    """A simple rich text resource type"""

    @classmethod
    def resource_model(cls) -> type["RichTextResource"]:
        return RichTextResource

    @classmethod
    def content_model(cls) -> type["RichTextContent"]:
        return RichTextContent


class GeneralRichTextResourceConfig(ModelBase):
    default_collapsed: Annotated[
        bool,
        Field(
            description=(
                "Whether contents of this resource should be collapsed by default"
            )
        ),
    ] = True


class RichTextResourceConfig(ResourceConfigBase):
    general: GeneralRichTextResourceConfig = GeneralRichTextResourceConfig()


class RichTextResource(ResourceBase):
    resource_type: Literal["richText"]  # camelCased resource type classname
    config: RichTextResourceConfig = RichTextResourceConfig()


class RichTextContent(ContentBase):
    """A content of a rich text resource"""

    resource_type: Literal["richText"]  # camelCased resource type classname
    html: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400, strip_whitespace=True),
        Field(
            description="HTML content of the rich text content object",
        ),
    ]
