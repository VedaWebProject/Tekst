import csv

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from beanie import PydanticObjectId
from beanie.operators import Eq, In
from pydantic import BeforeValidator, Field, StringConstraints

from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import CreateBase, ModelBase, ReadBase, make_update_model
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.precomputed import PrecomputedDataDocument
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
    ResourceReadExtras,
)
from tekst.models.resource_configs import (
    GeneralResourceConfig,
    ItemIntegrationConfig,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceTypeBase
from tekst.types import (
    ExcludeFromModelVariants,
    SchemaOptionalNonNullable,
    SingleLineString,
)
from tekst.utils import ensure


if TYPE_CHECKING:
    from tekst.models.search import ResourceSearchQuery


class LocationMetadata(ResourceTypeBase):
    """A resource type for key-value location metadata"""

    @classmethod
    def resource_model(cls) -> type["LocationMetadataResource"]:
        return LocationMetadataResource

    @classmethod
    def content_model(cls) -> type["LocationMetadataContent"]:
        return LocationMetadataContent

    @classmethod
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        return {
            "entries": {
                "type": "nested",
                "properties": {
                    "key": {"type": "keyword"},
                    "value": {
                        "type": "keyword",
                        "normalizer": "no_diacritics_normalizer",
                        "fields": {
                            "strict": {
                                "type": "keyword",
                                "normalizer": "lowercase_normalizer",
                            }
                        },
                    },
                },
            },
            "quick_search_content": {
                "type": "text",
                "analyzer": lenient_analyzer,
                "fields": {
                    "strict": {
                        "type": "text",
                        "analyzer": strict_analyzer,
                    }
                },
            },
        }

    @classmethod
    def _rtype_index_doc(
        cls,
        content: ContentBase,
    ) -> dict[str, Any] | None:
        if not isinstance(content, LocationMetadataContent):  # pragma: no cover
            raise ValueError(f"Expected LocationMetadataContent, got {type(content)}")
        return {
            "entries": [
                {
                    "key": entry.key,
                    "value": entry.value[0] if len(entry.value) == 1 else entry.value,
                }
                for entry in content.entries
            ],
            "quick_search_content": "; ".join(
                str(", ".join(entry.value)) for entry in content.entries
            ),
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        assert isinstance(query.resource_type_specific, LocationMetadataSearchQuery)
        es_queries = []
        strict_suffix = ".strict" if strict else ""
        res_id = str(query.common.resource_id)

        entries_usr_q = query.resource_type_specific.entries or []

        # process entries queries
        for entry_q in entries_usr_q:
            if not entry_q.key:
                continue  # pragma: no cover

            if entry_q.key and not entry_q.value:
                # only key is set (and no value): query for existence of key
                entry_k_q = {"term": {f"resources.{res_id}.entries.key": entry_q.key}}
                es_queries.append(
                    {
                        "nested": {
                            "path": f"resources.{res_id}.entries",
                            "query": entry_k_q,
                        }
                    }
                )
            elif entry_q.key and entry_q.value:
                # both key and value are set: query for specific key/value combination
                entry_k_q = {"term": {f"resources.{res_id}.entries.key": entry_q.key}}
                entry_v_q = (
                    {
                        "wildcard": {
                            (f"resources.{res_id}.entries.value{strict_suffix}"): {
                                "value": entry_q.value,
                            }
                        }
                    }
                    if entry_q.wildcards
                    else {
                        "term": {
                            (
                                f"resources.{res_id}.entries.value{strict_suffix}"
                            ): entry_q.value
                        }
                    }
                )
                es_queries.append(
                    {
                        "nested": {
                            "path": f"resources.{res_id}.entries",
                            "query": {
                                "bool": {"must": [entry_k_q, entry_v_q]},
                            },
                        }
                    }
                )

        return es_queries

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        content_ids: list[PydanticObjectId],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        if export_format == "csv":
            await cls._export_csv(resource, content_ids, file_path)
        else:  # pragma: no cover
            raise ValueError(
                f"Unsupported export format '{export_format}' "
                f"for resource type '{cls.get_key()}'"
            )

    @classmethod
    async def _export_csv(
        cls,
        resource: "LocationMetadataResourceDocument",
        content_ids: list[PydanticObjectId],
        file_path: Path,
    ) -> None:
        text = ensure(await TextDocument.get(resource.text_id))
        # construct labels of all locations on the resource's level
        full_loc_labels = await text.full_location_labels(resource.level)
        sort_num = 0
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(
                csvfile,
                dialect="excel",
                quoting=csv.QUOTE_MINIMAL,
            )
            aggs = await PrecomputedDataDocument.find_one(
                PrecomputedDataDocument.ref_id == resource.id,
                PrecomputedDataDocument.precomputed_type == "aggregations",
            )
            # get sorted items keys based on resource config
            keys = resource.config.special.entries_integration.sorted_item_keys(
                [agg["key"] for agg in aggs.data] if aggs and aggs.data else []
            )
            csv_writer.writerow(
                [
                    "LOCATION",
                    "SORT",
                    *keys,
                    "COMMENTS",
                ]
            )
            async for content in ContentBaseDocument.find(
                In(ContentBaseDocument.id, content_ids),
                with_children=True,
            ):
                entries_map = {entry.key: entry.value for entry in content.entries}
                values = [";".join(entries_map.get(key, "")) for key in keys]
                csv_writer.writerow(
                    [
                        full_loc_labels.get(str(content.location_id), ""),
                        sort_num,
                        *values,
                        content.comments_for_csv(),
                    ]
                )
                sort_num += 1


class LocationMetadataModGeneralConfig(GeneralResourceConfig):
    enable_content_context: Annotated[
        Literal[False],
        Field(
            description=(
                "Whether contents of this resource should be available for the parent "
                "level (always false for location metadata resources)"
            ),
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
        SchemaOptionalNonNullable,
    ] = False
    searchable_quick: Annotated[
        bool,
        Field(
            description=(
                "Whether this resource should be included in quick search "
                "(default false for location metadata resources)"
            ),
        ),
        SchemaOptionalNonNullable,
    ] = False


type LocationMetadataEntryKey = Annotated[
    str,
    StringConstraints(min_length=1, max_length=32),
    SingleLineString,
    Field(description="Key of the entry"),
]


type LocationMetadataEntryValue = Annotated[
    str,
    StringConstraints(min_length=1, max_length=256),
    SingleLineString,
    Field(description="Value of an entry"),
]


class LocationMetadataSpecialConfig(ModelBase):
    embed_as_tags: Annotated[
        bool,
        Field(description="Display metadata as tags in browse view"),
        SchemaOptionalNonNullable,
    ] = False
    entries_integration: ItemIntegrationConfig = ItemIntegrationConfig()


class LocationMetadataResourceConfig(ResourceConfigBase):
    general: LocationMetadataModGeneralConfig = LocationMetadataModGeneralConfig()
    special: LocationMetadataSpecialConfig = LocationMetadataSpecialConfig()


class LocationMetadataResource(ResourceBase):
    resource_type: Literal["locationMetadata"]  # camelCased resource type classname
    config: LocationMetadataResourceConfig = LocationMetadataResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["quick_search_content"]

    @classmethod
    def create_model(cls):
        return LocationMetadataResourceCreate

    @classmethod
    def read_model(cls):
        return LocationMetadataResourceRead

    @classmethod
    def update_model(cls):
        return LocationMetadataResourceUpdate

    @classmethod
    def document_model(cls):
        return LocationMetadataResourceDocument


class LocationMetadataResourceCreate(LocationMetadataResource, CreateBase):
    pass


class LocationMetadataResourceRead(
    LocationMetadataResource,
    ResourceReadExtras,
    ReadBase,
):
    pass


LocationMetadataResourceUpdate = make_update_model(LocationMetadataResource)


class LocationMetadataResourceDocument(
    LocationMetadataResource,
    ResourceBaseDocument,
):
    async def _update_aggregations(self, *, force: bool = False) -> None:
        max_values_per_key = 250
        # get precomputed resource aggregations data, if present
        precomp_doc = await PrecomputedDataDocument.find_one(
            PrecomputedDataDocument.ref_id == self.id,
            PrecomputedDataDocument.precomputed_type == "aggregations",
        )
        if precomp_doc:
            if precomp_doc.created_at >= self.contents_changed_at and not force:
                log.debug(
                    f"Aggregations for resource {str(self.id)} up-to-date. Skipping."
                )
                return
        else:
            if not self.id:  # pragma: no cover
                raise RuntimeError(
                    "Resource must be saved before aggregations can be created"
                )
            # create new aggregations document
            precomp_doc = PrecomputedDataDocument(
                ref_id=self.id,
                precomputed_type="aggregations",
            )

        # aggregate distinct location metadata keys and values
        precomp_doc.data = (
            await ContentBaseDocument.find(
                ContentBaseDocument.resource_id == self.id,
                Eq(ContentBaseDocument.archived, False),
                with_children=True,
            )
            .aggregate(
                [
                    {"$project": {"entries": 1}},
                    {"$unwind": {"path": "$entries"}},
                    {"$unwind": {"path": "$entries.value"}},
                    # create one document for each metadata key,
                    # collecting all values and the key occurrence count
                    {
                        "$group": {
                            "_id": "$entries.key",
                            "values": {"$push": "$entries.value"},
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
                    # remove values array if it contains more than n items
                    {
                        "$set": {
                            "values": {
                                "$cond": {
                                    "if": {
                                        "$gt": [
                                            {"$size": "$values"},
                                            max_values_per_key,
                                        ]
                                    },
                                    "then": "$$REMOVE",
                                    "else": "$values",
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
        precomp_doc.created_at = datetime.now(UTC)
        await precomp_doc.save()

    async def resource_precompute_hook(
        self,
        *,
        force: bool = False,
    ) -> None:
        await super().resource_precompute_hook(force=force)
        op_id = log_op_start(f"Generate aggregations for resource {str(self.id)}")
        try:
            await self._update_aggregations(force=force)
        except Exception as e:  # pragma: no cover
            log_op_end(op_id, failed=True)
            raise e
        log_op_end(op_id)


class LocationMetadataEntry(ModelBase):
    key: LocationMetadataEntryKey
    value: Annotated[
        list[LocationMetadataEntryValue],
        Field(
            min_length=1,
            max_length=64,
        ),
        BeforeValidator(lambda v: [v] if isinstance(v, str) else v),
    ]


class LocationMetadataContent(ContentBase):
    """A content of an audio resource"""

    resource_type: Literal["locationMetadata"]  # camelCased resource type classname
    entries: Annotated[
        list[LocationMetadataEntry],
        Field(
            min_length=1,
            max_length=128,
            description="List of metadata entries for a certain location",
        ),
    ]

    @classmethod
    def create_model(cls):
        return LocationMetadataContentCreate

    @classmethod
    def read_model(cls):
        return LocationMetadataContentRead

    @classmethod
    def update_model(cls):
        return LocationMetadataContentUpdate

    @classmethod
    def document_model(cls):
        return LocationMetadataContentDocument


class LocationMetadataContentCreate(LocationMetadataContent, CreateBase):
    pass


class LocationMetadataContentRead(LocationMetadataContent, ReadBase):
    pass


LocationMetadataContentUpdate = make_update_model(LocationMetadataContent)


class LocationMetadataContentDocument(LocationMetadataContent, ContentBaseDocument):
    pass


class LocationMetadataQueryEntry(ModelBase):
    key: Annotated[
        str | None,
        StringConstraints(max_length=32),
        SingleLineString,
        Field(
            alias="k",
            description="Metadata entry key query",
        ),
    ] = None
    value: Annotated[
        str | None,
        StringConstraints(max_length=256),
        SingleLineString,
        Field(
            alias="v",
            description="Metadata entry value query",
        ),
    ] = None
    wildcards: Annotated[
        bool,
        Field(
            alias="wc",
            description="Whether to interpret wildcards in the metadata value query",
        ),
    ] = False


class LocationMetadataSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["locationMetadata"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    entries: Annotated[
        list[LocationMetadataQueryEntry],
        Field(
            description="List of metadata queries",
            max_length=64,
        ),
        SchemaOptionalNonNullable,
    ] = []
