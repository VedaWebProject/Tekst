import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, StringConstraints, field_validator
from typing_extensions import TypeAliasType

from tekst.logs import log_op_end, log_op_start
from tekst.models.common import ModelBase, PydanticObjectId
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.resource import ResourceBase, ResourceExportFormat
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceBaseDocument, ResourceSearchQuery, ResourceTypeABC
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
    ) -> None:
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
                    {"$unwind": {"path": "$anno.value"}},
                    # create one document for each annotation key,
                    # collecting all values and the key occurrence count
                    {
                        "$group": {
                            "_id": "$anno.key",
                            "values": {"$push": "$anno.value"},
                            "keyOcc": {"$sum": 1},
                        }
                    },
                    # count per-key value occurrences on "values" field
                    {
                        "$set": {
                            "values": {
                                "$map": {
                                    "input": {"$setUnion": "$values"},
                                    "as": "v",
                                    "in": {
                                        "value": "$$v",
                                        "count": {
                                            "$size": {
                                                "$filter": {
                                                    "input": "$values",
                                                    "cond": {"$eq": ["$$this", "$$v"]},
                                                }
                                            }
                                        },
                                    },
                                }
                            }
                        }
                    },
                    # sort values array by count
                    {
                        "$set": {
                            "values": {
                                "$sortArray": {
                                    "input": "$values",
                                    "sortBy": {"count": -1},
                                }
                            }
                        }
                    },
                    # sort docs by key occurrence
                    {"$sort": {"keyOcc": -1}},
                    # remove values array if it contains more than 100 items
                    {
                        "$set": {
                            "values": {
                                "$cond": {
                                    "if": {"$gt": [{"$size": "$values"}, 100]},
                                    "then": "$$REMOVE",
                                    "else": "$values",
                                }
                            }
                        }
                    },
                    # project to final doc format,
                    # with values array only containing the values
                    {
                        "$project": {
                            "_id": 0,
                            "key": "$_id",
                            "values": {
                                "$map": {
                                    "input": "$values",
                                    "as": "v",
                                    "in": "$$v.value",
                                }
                            },
                        }
                    },
                ]
            )
            .to_list()
        )

        # update aggregations in DB
        resource_doc.aggregations = anno_aggs
        await resource_doc.replace()

    @classmethod
    async def contents_changed_hook(
        cls,
        resource_id: PydanticObjectId,
    ) -> None:
        op_id = log_op_start(f"Generate aggregations for resource {resource_id}")
        try:
            await cls._update_aggregations(resource_id)
        except Exception as e:
            log_op_end(op_id, failed=True)
            raise e
        log_op_end(op_id)

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""
        res_id = str(query.common.resource_id)

        if (
            not query.resource_type_specific.token.strip("* ")
            and not query.resource_type_specific.annotations
        ):
            # handle empty/match-all query (query for existing target resource field)
            es_queries.append(
                {
                    "nested": {
                        "path": f"resources.{res_id}.tokens",
                        "query": {
                            "exists": {
                                "field": f"resources.{res_id}.tokens.token",
                            }
                        },
                    }
                }
            )
        else:
            # construct token query
            token_query = (
                {
                    "simple_query_string": {
                        "fields": [f"resources.{res_id}.tokens.token{strict_suffix}"],
                        "query": query.resource_type_specific.token,
                    }
                }
                if query.resource_type_specific.token
                else None
            )
            # construct annotation queries
            anno_queries = []
            for anno in query.resource_type_specific.annotations:
                if not anno.value:
                    # if only key is set (and no value),
                    # query for the existence of the key
                    anno_queries.append(
                        {
                            "exists": {
                                "field": (
                                    f"resources.{res_id}.tokens.annotations.{anno.key}"
                                ),
                            }
                        }
                    )
                elif anno.value == "__missing__":
                    # if value is set to "__missing__", we're looking for tokens
                    # that specifically DON'T have an annotation with the given key
                    anno_queries.append(
                        {
                            "bool": {
                                "must_not": {
                                    "exists": {
                                        "field": (
                                            f"resources.{res_id}"
                                            f".tokens.annotations.{anno.key}"
                                        ),
                                    }
                                }
                            }
                        }
                    )
                else:
                    # if both key and value are set,
                    # query for the specific key/value combination
                    anno_queries.append(
                        {
                            "simple_query_string": {
                                "fields": [
                                    f"resources.{res_id}.tokens.annotations.{anno.key}"
                                ],
                                "query": anno.value,
                            }
                        }
                    )

            # add token and annotation queries to the ES query
            es_queries.append(
                {
                    "nested": {
                        "path": f"resources.{res_id}.tokens",
                        "query": {
                            "bool": {
                                "must": [
                                    *([token_query] if token_query else []),
                                    *anno_queries,
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
                        "normalizer": "no_diacritics_normalizer",
                        "fields": {"strict": {"type": "keyword"}},
                    }
                },
            },
        }

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "TextAnnotationContent",
    ) -> dict[str, Any]:
        return {
            "tokens": [
                {
                    "token": token.token or "",
                    "annotations": {
                        anno.key: anno.value[0] if len(anno.value) == 1 else anno.value
                        for anno in token.annotations
                    }
                    if token.annotations
                    else None,
                }
                for token in content.tokens
            ],
        }

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list["TextAnnotationContent"],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        if export_format == "csv":
            await cls._export_csv(resource, contents, file_path)
        else:
            raise ValueError(
                f"Unsupported export format '{export_format}' "
                f"for resource type '{cls.get_key()}'"
            )

    @classmethod
    async def _export_csv(
        cls,
        resource: "TextAnnotationResource",
        contents: list["TextAnnotationContent"],
        file_path: Path,
    ) -> None:
        text = await TextDocument.get(resource.text_id)
        # construct labels of all locations on the resource's level
        full_location_labels = await text.full_location_labels(resource.level)
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(
                csvfile,
                dialect="excel",
                quoting=csv.QUOTE_ALL,
            )
            anno_keys = sorted(list({agg.key for agg in resource.aggregations}))
            csv_writer.writerow(
                ["LOCATION", "TOKEN", "POSITION", *anno_keys, "COMMENT"]
            )
            for content in contents:
                for i, token in enumerate(content.tokens):
                    token_annos = {
                        anno.key: anno.value for anno in token.annotations or []
                    }
                    csv_annos = [
                        token_annos.get(anno_key, "") for anno_key in anno_keys
                    ]
                    csv_writer.writerow(
                        [
                            full_location_labels.get(str(content.location_id), ""),
                            token.token,
                            i,
                            *csv_annos,
                            content.comment,
                        ]
                    )


class GeneralTextAnnotationResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType = None


class TextAnnotationResourceConfig(ResourceConfigBase):
    general: GeneralTextAnnotationResourceConfig = GeneralTextAnnotationResourceConfig()
    display_template: Annotated[
        str | None,
        Field(
            max_length=2048,
            description=(
                "Template string used for displaying the annotations in the web client "
                "(if missing, all annotations are displayed with key and value, "
                "separated by commas)"
            ),
        ),
        val.CleanupMultiline,
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


TextAnnotationValue = TypeAliasType(
    "TextAnnotationValue",
    Annotated[
        str,
        Field(
            description="Value of an annotation",
        ),
        BeforeValidator(lambda v: str(v) if v is not None else None),
        StringConstraints(
            min_length=1,
            max_length=256,
            strip_whitespace=True,
        ),
    ],
)

TextAnnotationValues = TypeAliasType(
    "TextAnnotationValues",
    Annotated[
        list[TextAnnotationValue],
        Field(
            description="List of values of an annotation",
            min_length=1,
            max_length=64,
        ),
        BeforeValidator(lambda v: [v] if isinstance(v, str) else v),
    ],
)


class TextAnnotationEntry(ModelBase):
    key: Annotated[
        str,
        Field(
            description="Key of the annotation",
        ),
        BeforeValidator(lambda v: str(v) if v is not None else None),
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        TextAnnotationValues,
        Field(
            description="Value(s) of the annotation",
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
    @classmethod
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
    lb: Annotated[
        bool,
        Field(description="Whether this token ends a line"),
    ] = False


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
