from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import (
    DeepLLinksConfig,
    DefaultCollapsedConfigType,
    FontConfigType,
    ReducedViewOnelineConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.utils import validators as val


class PlainText(ResourceTypeABC):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent

    @classmethod
    def search_query_model(cls) -> type["PlainTextSearchQuery"]:
        return PlainTextSearchQuery

    @classmethod
    def construct_es_queries(
        cls, query: ResourceSearchQuery, *, strict: bool = False
    ) -> list[dict[str, Any]]:
        es_queries = []
        set_fields = query.get_set_fields()
        strict_suffix = ".strict" if strict else ""
        if "text" in set_fields:
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [f"{query.common.resource_id}.text{strict_suffix}"],
                        "query": query.resource_type_specific.text,
                    }
                }
            )
        if "comment" in set_fields:
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            f"{query.common.resource_id}.comment{strict_suffix}"
                        ],
                        "query": query.common.comment,
                    }
                }
            )
        return es_queries

    @classmethod
    def index_doc_properties(cls) -> dict[str, Any]:
        return {
            "text": {
                "type": "text",
                "analyzer": "standard_asciifolding",
                "fields": {"strict": {"type": "text"}},
            },
        }

    @classmethod
    def index_doc_data(cls, content: "PlainTextContent") -> dict[str, Any]:
        return content.model_dump(include={"text"})


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    reduced_view_oneline: ReducedViewOnelineConfigType = False
    font: FontConfigType = None


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


class PlainTextSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["plainText"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    text: Annotated[
        str,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = ""
