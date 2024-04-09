from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, field_validator

from tekst.logging import log
from tekst.models.common import ModelBase, PydanticObjectId
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
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
    async def _update_aggregations(cls, resource_id: PydanticObjectId) -> None:
        log.debug(f"Updating aggregations for resource {resource_id}...")

        # get resource document
        rs_doc_model = cls.resource_model().document_model()
        resource_doc = await rs_doc_model.get(resource_id)
        if not resource_doc:
            return

        # group annotations
        anno_aggs = (
            await ContentBaseDocument.find(
                ContentBaseDocument.resource_id == resource_id,
                with_children=True,
            )
            .aggregate(
                [
                    {"$project": {"anno": "$tokens.annotations"}},
                    {"$unwind": {"path": "$anno"}},
                    {"$unwind": {"path": "$anno"}},
                    {
                        "$group": {
                            "_id": "$anno.key",
                            "collected": {"$push": "$anno.value"},  # collected values
                            "values": {"$addToSet": "$anno.value"},  # distinct values
                            "count": {"$sum": 1},  # key occurrence count
                        }
                    },
                    {"$sort": {"count": -1}},  # sort by key occurrence count
                    {
                        "$project": {
                            "_id": 0,
                            "key": "$_id",
                            "values": {
                                "$cond": {  # exclude if count of distict values > 100
                                    "if": {"$gt": [{"$size": "$values"}, 100]},
                                    "then": "$$REMOVE",
                                    "else": "$values",
                                }
                            },
                            "collected": {
                                "$cond": {  # exclude if count of distict values > 100
                                    "if": {"$gt": [{"$size": "$values"}, 100]},
                                    "then": "$$REMOVE",
                                    "else": "$collected",
                                }
                            },
                        },
                    },
                ]
            )
            .to_list()
        )

        # sort annotation values ("values") by occurrence count (from "collected")
        # (couldn't manage to do that in DB aggregations)
        for anno in anno_aggs:
            if "values" in anno:
                anno["values"].sort(
                    reverse=True,
                    key=lambda v: anno.get("collected", []).count(v),
                )
            if "collected" in anno:
                del anno["collected"]

        # update aggregations in DB
        resource_doc.aggregations = anno_aggs
        await resource_doc.replace()

        log.debug(f"Finished updating aggregations for resource {resource_id}...")

    @classmethod
    async def contents_changed_hook(cls, resource_id: PydanticObjectId) -> None:
        await cls._update_aggregations(resource_id)

    @classmethod
    def rtype_es_queries(
        cls, *, query: ResourceSearchQuery, strict: bool = False
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""

        if (
            not query.resource_type_specific.token
            and not query.resource_type_specific.annotations
        ):
            # handle empty/match-all query (query for existing target resource field)
            es_queries.append(
                {
                    "exists": {
                        "field": f"resources.{query.common.resource_id}",
                    }
                }
            )
        else:
            # contruct token query
            token_query = (
                {
                    "term": {
                        (
                            f"resources.{query.common.resource_id}"
                            f".tokens.token{strict_suffix}"
                        ): query.resource_type_specific.token
                    }
                }
                if query.resource_type_specific.token
                else None
            )
            # construct annotation queries
            annotation_queries = []
            for anno in query.resource_type_specific.annotations:
                if not anno.value:
                    # if only key is set (and no value),
                    # query for the existence of the key
                    annotation_queries.append(
                        {
                            "exists": {
                                "field": (
                                    f"resources.{query.common.resource_id}"
                                    f".tokens.annotations.{anno.key}"
                                ),
                            }
                        }
                    )
                else:
                    # if both key and value are set,
                    # query for the specific key/value combination
                    annotation_queries.append(
                        {
                            "term": {
                                (
                                    f"resources.{query.common.resource_id}"
                                    f".tokens.annotations.{anno.key}"
                                ): anno.value
                            }
                        }
                    )

            # add token and annotation queries to the ES query
            es_queries.append(
                {
                    "nested": {
                        "path": f"resources.{query.common.resource_id}.tokens",
                        "query": {
                            "bool": {
                                "must": [
                                    *([token_query] if token_query else []),
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
                    "token": token.token or "",
                    "annotations": {
                        anno.key: anno.value for anno in token.annotations or []
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
    display_template: Annotated[
        str | None,
        Field(
            min_length=8,
            max_length=2048,
            description=(
                "Template string used for displaying the annotations in the web client "
                "(if missing, all annotations are displayed with key and value, "
                "separated by commas)"
            ),
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = None


class AnnotationAggregationGroup(ModelBase):
    key: str
    values: list[str] | None = None


class TextAnnotationResource(ResourceBase):
    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    config: TextAnnotationResourceConfig = TextAnnotationResourceConfig()
    aggregations: Annotated[
        list[AnnotationAggregationGroup] | None,
        Field(
            description="Aggregated groups for this resource's annotations",
        ),
    ] = None


class TextAnnotationEntry(ModelBase):
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


class TextAnnotationQueryEntry(ModelBase):
    key: Annotated[
        str,
        Field(
            alias="k",
            description="Key of the annotation",
        ),
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        str | None,
        Field(
            alias="v",
            description="Value of the annotation",
        ),
        StringConstraints(
            max_length=64,
            strip_whitespace=True,
        ),
    ] = None

    @field_validator("key", "value", mode="before")
    def strip_whitespace(cls, v) -> str:
        return str(v) if v else ""


class TextAnnotationToken(ModelBase):
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
        list[TextAnnotationQueryEntry],
        Field(
            alias="anno",
            description="List of annotations to match",
            max_length=64,
        ),
    ] = []
