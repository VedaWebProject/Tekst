import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.types import (
    ConStr,
    ConStrOrNone,
    HttpUrl,
    SchemaOptionalNullable,
)


class ExternalReferences(ResourceTypeABC):
    """A resource type for external references"""

    @classmethod
    def resource_model(cls) -> type["ExternalReferencesResource"]:
        return ExternalReferencesResource

    @classmethod
    def content_model(cls) -> type["ExternalReferencesContent"]:
        return ExternalReferencesContent

    @classmethod
    def search_query_model(cls) -> type[ResourceSearchQuery] | None:
        return ExternalReferencesSearchQuery

    @classmethod
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        return {
            "text": {
                "type": "text",
                "analyzer": lenient_analyzer,
                "fields": {
                    "strict": {
                        "type": "text",
                        "analyzer": strict_analyzer,
                    }
                },
                "index_prefixes": {},
            },
        }

    @classmethod
    def _rtype_index_doc(
        cls,
        content: "ExternalReferencesContent",
    ) -> dict[str, Any] | None:
        return {
            "text": [
                "".join(
                    [
                        f"{f.get('title', '')}",
                        f" ({f.get('alt_ref')})" if f.get("alt_ref") else "",
                        f" – {f.get('description')}" if f.get("description") else "",
                    ]
                ).strip()
                for f in content.model_dump(include={"links"}).get("links", [])
            ]
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ExternalReferencesSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        es_queries = []

        # add query only if not "empty"
        if query.resource_type_specific.text.strip("* "):
            strict_suffix = ".strict" if strict else ""
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            f"resources.{str(query.common.resource_id)}.text{strict_suffix}"
                        ],
                        "query": query.resource_type_specific.text,
                        "analyze_wildcard": True,
                    }
                }
            )
        return es_queries

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list["ExternalReferencesContent"],
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
        resource: "ExternalReferencesResource",
        contents: list["ExternalReferencesContent"],
        file_path: Path,
    ) -> None:
        text = await TextDocument.get(resource.text_id)
        # construct labels of all locations on the resource's level
        full_loc_labels = await text.full_location_labels(resource.level)
        sort_num = 0
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(
                csvfile,
                dialect="excel",
                quoting=csv.QUOTE_MINIMAL,
            )
            csv_writer.writerow(
                [
                    "LOCATION",
                    "SORT",
                    "URL",
                    "TITLE",
                    "DESCRIPTION",
                    "ALT_REF",
                    "AUTHORS_COMMENT",
                    "EDITORS_COMMENT",
                ]
            )
            for content in contents:
                for link in content.links:
                    csv_writer.writerow(
                        [
                            full_loc_labels.get(str(content.location_id), ""),
                            sort_num,
                            link.url,
                            link.title,
                            link.description,
                            link.alt_ref,
                            content.authors_comment,
                            content.editors_comment,
                        ]
                    )
                    sort_num += 1


class ExternalReferencesResourceConfig(ResourceConfigBase):
    pass


class ExternalReferencesResource(ResourceBase):
    resource_type: Literal["externalReferences"]  # camelCased resource type classname
    config: ExternalReferencesResourceConfig = ExternalReferencesResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["text"]


class ExternalReferencesLink(ModelBase):
    url: Annotated[
        HttpUrl,
        Field(
            description="URL of the link",
        ),
    ]
    title: Annotated[
        ConStr(
            max_length=128,
            cleanup="oneline",
        ),
        Field(
            description="Title/text of the link",
        ),
    ]
    description: Annotated[
        ConStrOrNone(
            max_length=4096,
            cleanup="multiline",
        ),
        Field(
            description="Description of the link",
        ),
    ] = None
    alt_ref: Annotated[
        ConStrOrNone(
            max_length=512,
            cleanup="oneline",
        ),
        Field(
            description="Additional, alternate reference data",
        ),
    ] = None


class ExternalReferencesContent(ContentBase):
    """A content of an external reference resource"""

    resource_type: Literal["externalReferences"]  # camelCased resource type classname
    links: Annotated[
        list[ExternalReferencesLink],
        Field(
            description="List of external reference link objects",
            min_length=1,
            max_length=100,
        ),
    ]


class ExternalReferencesSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["externalReferences"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    text: Annotated[
        ConStr(
            min_length=0,
            max_length=512,
            cleanup="oneline",
        ),
        Field(
            description="Text to search for",
        ),
        SchemaOptionalNullable,
    ] = ""
