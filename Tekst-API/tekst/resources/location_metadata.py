import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field
from typing_extensions import TypeAliasType, TypedDict

from tekst.i18n import TranslationBase, Translations
from tekst.models.common import (
    ModelBase,
)
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    CommonResourceConfig,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.types import (
    ConStr,
    ConStrOrNone,
    ExcludeFromModelVariants,
    SchemaOptionalNonNullable,
    SchemaOptionalNullable,
)


class LocationMetadata(ResourceTypeABC):
    """A resource type for key-value location metadata"""

    @classmethod
    def resource_model(cls) -> type["LocationMetadataResource"]:
        return LocationMetadataResource

    @classmethod
    def content_model(cls) -> type["LocationMetadataContent"]:
        return LocationMetadataContent

    @classmethod
    def search_query_model(cls) -> type[ResourceSearchQuery]:
        return LocationMetadataSearchQuery

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
                    "key": {
                        "type": "keyword",
                    },
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
            "entries_concat": {
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
        content: "LocationMetadataContent",
    ) -> dict[str, Any] | None:
        return {
            "entries": [
                {
                    "key": entry.key,
                    "value": entry.value[0] if len(entry.value) == 1 else entry.value,
                }
                for entry in content.entries
            ],
            "entries_concat": "; ".join(str(entry.value) for entry in content.entries),
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "LocationMetadataSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        es_queries = []
        strict_suffix = ".strict" if strict else ""
        res_id = str(query.common.resource_id)

        entries_usr_q = query.resource_type_specific.entries or []

        # process entries queries
        for entry_q in entries_usr_q:
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
                            (f"resources.{res_id}.entries" f".value{strict_suffix}"): {
                                "value": entry_q.value,
                            }
                        }
                    }
                    if entry_q.wildcards
                    else {
                        "term": {
                            (
                                f"resources.{res_id}.entries" f".value{strict_suffix}"
                            ): entry_q.value
                        }
                    }
                )
                es_queries.append(
                    {
                        "nested": {
                            "path": f"resources.{res_id}.entries",
                            "query": {
                                "bool": {
                                    "must": [entry_k_q, entry_v_q],
                                },
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
        contents: list["LocationMetadataContent"],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        if export_format == "csv":
            await cls._export_csv(resource, contents, file_path)
        else:  # pragma: no cover
            raise ValueError(
                f"Unsupported export format '{export_format}' "
                f"for resource type '{cls.get_key()}'"
            )

    @classmethod
    async def _export_csv(
        cls,
        resource: "LocationMetadataResource",
        contents: list["LocationMetadataContent"],
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
            csv_writer.writerow(
                ["LOCATION"]
                + [entry.key for entry in contents.entries]
                + ["LOCATION_COMMENT"]
            )
            for content in contents:
                for audio_file in content.files:
                    csv_writer.writerow(
                        [full_location_labels.get(str(content.location_id), "")]
                        + [entry.value for entry in contents.entries]
                        + [content.comment]
                    )


class LocationMetadataModifiedCommonResourceConfig(CommonResourceConfig):
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


LocationMetadataEntryKey = TypeAliasType(
    "LocationMetadataEntryValue",
    Annotated[
        ConStr(
            max_length=32,
            cleanup="oneline",
        ),
        Field(
            description="Key of the entry",
        ),
    ],
)


LocationMetadataEntryValue = TypeAliasType(
    "LocationMetadataEntryValue",
    Annotated[
        ConStr(
            max_length=256,
            cleanup="oneline",
        ),
        Field(
            description="Value of an entry",
        ),
    ],
)


class MetadataKeyTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Translation of a metadata entry key",
        ),
    ]


class LocationMetadataSpecialConfig(ModelBase):
    """Config properties specific to the location metadata resource type"""

    key_translations: Annotated[
        dict[LocationMetadataEntryKey, Translations[MetadataKeyTranslation]],
        Field(
            description=(
                "Translations for the keys used in this location metadata resource"
            ),
            min_length=1,
            max_length=512,
        ),
    ] = []


class LocationMetadataResourceConfig(ResourceConfigBase):
    common: LocationMetadataModifiedCommonResourceConfig = (
        LocationMetadataModifiedCommonResourceConfig()
    )
    location_metadata: LocationMetadataSpecialConfig = LocationMetadataSpecialConfig()


class LocationMetadataResource(ResourceBase):
    resource_type: Literal["locationMetadata"]  # camelCased resource type classname
    config: LocationMetadataResourceConfig = LocationMetadataResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["entries_concat"]


class LocationMetadataEntry(TypedDict):
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


class LocationMetadataQueryEntry(ModelBase):
    key: Annotated[
        ConStr(
            max_length=32,
            cleanup="oneline",
        ),
        Field(
            alias="k",
            description="Metadata entry key query",
        ),
    ]
    value: Annotated[
        ConStrOrNone(
            min_length=0,
            max_length=256,
            cleanup="oneline",
        ),
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
        SchemaOptionalNullable,
    ] = []
