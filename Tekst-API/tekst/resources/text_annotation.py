from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints
from typing_extensions import TypedDict

from tekst.logging import log
from tekst.models.common import ModelBase, PydanticObjectId
from tekst.models.content import ContentBase, ContentBaseDocument
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
    async def _update_aggregations(
        cls,
        resource_id: PydanticObjectId,
        in_sync_with: Literal["db", "index"] = "db",
    ) -> None:
        log.debug(
            "Updating aggregations for resource "
            f"{resource_id} (sync: {in_sync_with})..."
        )

        # get resource document
        rs_doc_model = cls.resource_model().document_model()
        resource_doc = await rs_doc_model.get(resource_id)
        if not resource_doc:
            return

        # check if we can reuse aggregations based on last db change
        if resource_doc.aggregations_db and in_sync_with == "index":
            resource_doc.aggregations_index = resource_doc.aggregations_db
            await resource_doc.replace()
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
                            "values": 1,
                            "collected": 1,
                        },
                    },
                ]
            )
            .to_list()
        )

        # sort annotation values ("values") by occurrence count (from "collected")
        # (couldn't manage to do that in DB aggregations)
        for anno in anno_aggs:
            anno["values"].sort(
                reverse=True,
                key=lambda v: anno.get("collected", []).count(v),
            )
            del anno["collected"]

        # update aggregations in DB
        if in_sync_with == "db":
            resource_doc.aggregations_db = anno_aggs
        elif in_sync_with == "index":
            resource_doc.aggregations_index = anno_aggs
        await resource_doc.replace()

    @classmethod
    async def content_changed_hook(cls, resource_id: PydanticObjectId) -> None:
        await cls._update_aggregations(resource_id, "db")

    @classmethod
    async def index_updated_hook(cls, resource_id: PydanticObjectId) -> None:
        await cls._update_aggregations(resource_id, "index")

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


class AnnotationGroup(TypedDict):
    key: str
    values: list[str]


class TextAnnotationResource(ResourceBase):
    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    config: TextAnnotationResourceConfig = TextAnnotationResourceConfig()
    aggregations_db: Annotated[
        list[AnnotationGroup] | None,
        Field(
            description=(
                "Aggregated groups for this resource's "
                "annotations, in sync with the database"
            ),
        ),
    ] = None
    aggregations_index: Annotated[
        list[AnnotationGroup] | None,
        Field(
            description=(
                "Aggregated groups for this resource's "
                "annotations, in sync with the search index"
            ),
        ),
    ] = None


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


class TextAnnotationQueryEntry(TypedDict):
    key: Annotated[
        str | None,
        Field(
            description="Key of the annotation",
        ),
        StringConstraints(
            max_length=32,
            strip_whitespace=True,
        ),
    ] = None
    value: Annotated[
        str | None,
        Field(
            description="Value of the annotation",
        ),
        StringConstraints(
            max_length=64,
            strip_whitespace=True,
        ),
    ] = None


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
        list[TextAnnotationQueryEntry],
        Field(
            alias="anno",
            description="List of annotations to match",
            max_length=64,
        ),
    ] = ""
