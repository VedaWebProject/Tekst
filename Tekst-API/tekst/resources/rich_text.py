from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase, ResourceSearchQueryBase
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceTypeABC
from tekst.utils import validators as val


class RichText(ResourceTypeABC):
    """A simple rich text resource type"""

    @classmethod
    def resource_model(cls) -> type["RichTextResource"]:
        return RichTextResource

    @classmethod
    def content_model(cls) -> type["RichTextContent"]:
        return RichTextContent

    @classmethod
    def search_query_model(cls) -> type["RichTextSearchQuery"]:
        return RichTextSearchQuery

    @classmethod
    def index_doc_properties(cls) -> dict[str, Any]:
        return {
            "html": {
                "type": "text",
                "analyzer": "standard_htmlstrip_asciifolding",
                "fields": {
                    "strict": {"type": "text", "analyzer": "standard_htmlstrip"}
                },
            },
        }

    @classmethod
    def index_doc_data(cls, content: "RichTextContent") -> dict[str, Any]:
        return content.model_dump(
            include={
                "html",
            }
        )


class GeneralRichTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = True
    font: FontConfigType = None


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
        StringConstraints(max_length=102400, strip_whitespace=True),
        Field(
            description="HTML content of the rich text content object",
        ),
    ]
    editor_mode: Annotated[
        Literal["wysiwyg", "html"],
        Field(description="Last used editor mode for this content"),
    ] = "wysiwyg"


class RichTextSearchQuery(ResourceSearchQueryBase):
    html: Annotated[
        str | None,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = None
    comment: Annotated[
        str | None,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = None
