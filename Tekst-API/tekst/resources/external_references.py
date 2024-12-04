import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase, SchemaOptionalNonNullable
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.utils import validators as val


class ExternalReferences(ResourceTypeABC):
    """A resource type for external references"""

    @classmethod
    def resource_model(cls) -> type["ExternalReferencesResource"]:
        return ExternalReferencesResource

    @classmethod
    def content_model(cls) -> type["ExternalReferencesContent"]:
        return ExternalReferencesContent

    @classmethod
    def search_query_model(cls) -> type["ExternalReferencesSearchQuery"]:
        return ExternalReferencesSearchQuery

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "text": {
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {"strict": {"type": "text"}},
                "index_prefixes": {},
            },
        }

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "ExternalReferencesContent",
    ) -> dict[str, Any]:
        return {
            "text": [
                f"{f.get('title', '')} – {f.get('description', '')}".strip()
                for f in content.model_dump(include={"links"}).get("links", [])
            ]
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""

        if not query.resource_type_specific.text.strip("* "):
            # handle empty/match-all query (query for existing target field)
            es_queries.append(
                {
                    "exists": {
                        "field": f"resources.{str(query.common.resource_id)}",
                    }
                }
            )
        else:
            # handle actual query with content
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
        full_location_labels = await text.full_location_labels(resource.level)
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(
                csvfile,
                dialect="excel",
                quoting=csv.QUOTE_ALL,
            )
            csv_writer.writerow(
                [
                    "LOCATION",
                    "URL",
                    "TITLE",
                    "DESCRIPTION",
                    "LOCATION_COMMENT",
                ]
            )
            for content in contents:
                for link in content.links:
                    csv_writer.writerow(
                        [
                            full_location_labels.get(str(content.location_id), ""),
                            link.url,
                            link.title,
                            link.description,
                            content.comment,
                        ]
                    )


class GeneralExternalReferencesResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType = None


class ExternalReferencesResourceConfig(ResourceConfigBase):
    general: GeneralExternalReferencesResourceConfig = (
        GeneralExternalReferencesResourceConfig()
    )


class ExternalReferencesResource(ResourceBase):
    resource_type: Literal["externalReferences"]  # camelCased resource type classname
    config: ExternalReferencesResourceConfig = ExternalReferencesResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["text"]


class ExternalReferencesLink(ModelBase):
    url: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=2083,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
        Field(
            description="URL of the link",
        ),
    ]
    title: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=128,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
        Field(
            description="Title/text of the link",
        ),
    ]
    description: Annotated[
        str | None,
        StringConstraints(
            max_length=4096,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
        Field(
            description="Description of the link",
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
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        Field(
            description="Text to search for",
        ),
        val.CleanupOneline,
        SchemaOptionalNonNullable,
    ] = ""
