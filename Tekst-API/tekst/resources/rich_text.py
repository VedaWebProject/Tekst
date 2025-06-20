import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase, ResourceExportFormat
from tekst.models.resource_configs import (
    GeneralResourceConfig,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceBaseDocument, ResourceSearchQuery, ResourceTypeABC
from tekst.types import (
    CollapsibleContentsConfigValue,
    ConStr,
    ContentCssProperties,
    ExcludeFromModelVariants,
    SchemaOptionalNonNullable,
    SchemaOptionalNullable,
    SearchReplacements,
)
from tekst.utils.html import get_html_text, sanitize_html


class RichText(ResourceTypeABC):
    """A simple rich text resource type"""

    @classmethod
    def resource_model(cls) -> type["RichTextResource"]:
        return RichTextResource

    @classmethod
    def content_model(cls) -> type["RichTextContent"]:
        return RichTextContent

    @classmethod
    def search_query_model(cls) -> type[ResourceSearchQuery] | None:
        return RichTextSearchQuery

    @classmethod
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        return {
            "html": {
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
        content: "RichTextContent",
    ) -> dict[str, Any] | None:
        return {
            "html": get_html_text(content.html),
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "RichTextSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        es_queries = []

        # add query only if not "empty"
        if query.resource_type_specific.html.strip("* "):
            strict_suffix = ".strict" if strict else ""
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            (
                                f"resources.{str(query.common.resource_id)}"
                                f".html{strict_suffix}"
                            )
                        ],
                        "query": query.resource_type_specific.html,
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
        contents: list["RichTextContent"],
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
        resource: "RichTextResource",
        contents: list["RichTextContent"],
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
                    "HTML",
                    "AUTHORS_COMMENT",
                    "EDITORS_COMMENT",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_loc_labels.get(str(content.location_id), ""),
                        sort_num,
                        content.html,
                        content.authors_comment,
                        content.editors_comment,
                    ]
                )
                sort_num += 1


class RichTextModGeneralConfig(GeneralResourceConfig):
    collapsible_contents: CollapsibleContentsConfigValue = 400
    enable_content_context: Annotated[
        Literal[False],
        Field(
            description=(
                "Whether contents of this resource should be available for the parent "
                "level (always false for rich text resources)"
            ),
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
        SchemaOptionalNonNullable,
    ] = False


class RichTextSpecialConfig(ModelBase):
    search_replacements: SearchReplacements = []
    content_css: ContentCssProperties = []


class RichTextResourceConfig(ResourceConfigBase):
    general: RichTextModGeneralConfig = RichTextModGeneralConfig()
    special: RichTextSpecialConfig = RichTextSpecialConfig()


class RichTextResource(ResourceBase):
    resource_type: Literal["richText"]  # camelCased resource type classname
    config: RichTextResourceConfig = RichTextResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["html"]


class RichTextContent(ContentBase):
    """A content of a rich text resource"""

    resource_type: Literal["richText"]  # camelCased resource type classname
    html: Annotated[
        ConStr(
            max_length=102400,
        ),
        Field(
            description="HTML content of the rich text content object",
        ),
    ]
    editor_mode: Annotated[
        Literal["wysiwyg", "html"],
        Field(description="Last used editor mode for this content"),
    ] = "wysiwyg"

    @field_validator("html", mode="after")
    @classmethod
    def validate_html(cls, value) -> str:
        return sanitize_html(value)


class RichTextSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["richText"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    html: Annotated[
        ConStr(
            min_length=0,
            max_length=512,
            cleanup="oneline",
        ),
        Field(
            description="HTML text content search query",
        ),
        SchemaOptionalNullable,
    ] = ""
