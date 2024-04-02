from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints
from typing_extensions import TypedDict

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceTypeABC
from tekst.utils import validators as val


class TextAnnotation(ResourceTypeABC):
    """An annotation resource type for tokenized text"""

    @classmethod
    def resource_model(cls) -> type["TextAnnotationResource"]:
        return TextAnnotationResource

    @classmethod
    def content_model(cls) -> type["TextAnnotationContent"]:
        return TextAnnotationContent

    @classmethod
    def search_query_model(cls) -> type["TextAnnotationSearchQuery"]:
        return TextAnnotationSearchQuery

    @classmethod
    def rtype_es_queries(
        cls, *, query: "TextAnnotationSearchQuery", strict: bool = False
    ) -> list[dict[str, Any]]:
        es_queries = []
        if "tokens" in query.get_set_fields():
            token_query = {
                "term": {f"{query.common.resource_id}.tokens.token": query.token}
            }
            annotation_queries = [
                {
                    "term": {
                        f"{query.common.resource_id}.tokens.annotations.{key}": value
                    }
                }
                for key, value in query.annotations.items()
            ]
            es_queries.append(
                {
                    "nested": {
                        "path": f"{query.common.resource_id}.tokens",
                        "query": {
                            "bool": {
                                "must": [
                                    token_query,
                                    *annotation_queries,
                                ],
                            },
                        },
                    }
                }
            )
        return es_queries

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "tokens": {
                "type": "nested",
                "dynamic": True,
                "properties": {
                    "token": {
                        "type": "keyword",
                        "normalizer": "asciifolding_normalizer",
                        "fields": {"strict": {"type": "keyword"}},
                    }
                },
            },
        }

    @classmethod
    def rtype_index_doc_data(cls, content: "TextAnnotationContent") -> dict[str, Any]:
        return {
            "tokens": [
                {
                    "token": token.get("token", ""),
                    "annotations": {
                        anno["key"]: anno["value"]
                        for anno in token.get("annotations", [])
                    },
                }
                for token in content.tokens
            ],
        }


class GeneralTextAnnotationResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType | None = None


class TextAnnotationResourceConfig(ResourceConfigBase):
    general: GeneralTextAnnotationResourceConfig = GeneralTextAnnotationResourceConfig()
    # TODO: implement


class TextAnnotationResource(ResourceBase):
    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    config: TextAnnotationResourceConfig = TextAnnotationResourceConfig()


class TextAnnotationEntry(TypedDict):
    key: Annotated[
        str,
        Field(
            description="Key of the annotation",
        ),
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        str,
        Field(
            description="Value of the annotation",
        ),
        StringConstraints(
            min_length=1,
            max_length=64,
            strip_whitespace=True,
        ),
    ]


class TextAnnotationToken(TypedDict):
    token: Annotated[
        str,
        Field(
            description="Text token",
        ),
        StringConstraints(
            min_length=1,
            max_length=4096,
            strip_whitespace=True,
        ),
    ]
    annotations: Annotated[
        list[TextAnnotationEntry],
        Field(
            description="List of annotations on this token",
            max_length=128,
        ),
    ] = []


class TextAnnotationContent(ContentBase):
    """A content of a text annotation resource"""

    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    tokens: Annotated[
        list[TextAnnotationToken],
        Field(
            description="List of annotated tokens in this content object",
            max_length=1024,
        ),
    ]


class TextAnnotationSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["textAnnotation"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    token: Annotated[
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
    ] = ""
    annotations: Annotated[
        list[TextAnnotationEntry],
        Field(
            alias="anno",
            description="List of annotations to match",
            max_length=64,
        ),
    ] = ""
