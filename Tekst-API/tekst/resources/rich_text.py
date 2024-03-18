from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
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
    def construct_es_queries(
        cls, query: ResourceSearchQuery, *, strict: bool = False
    ) -> list[dict[str, Any]]:
        es_queries = []
        set_fields = query.get_set_fields()
        strict_suffix = ".strict" if strict else ""
        if "html" in set_fields:
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [f"{query.resource_id}.html{strict_suffix}"],
                        "query": query.html,
                    }
                }
            )
        if "comment" in set_fields:
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [f"{query.resource_id}.comment{strict_suffix}"],
                        "query": query.comment,
                    }
                }
            )
        return es_queries

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


class RichTextSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["richText"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    html: Annotated[
        str,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = ""
