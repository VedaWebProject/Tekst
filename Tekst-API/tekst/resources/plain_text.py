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
    ContentCssProperties,
    SchemaOptionalNullable,
    SearchReplacements,
)


class PlainText(ResourceTypeABC):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent

    @classmethod
    def search_query_model(cls) -> type[ResourceSearchQuery] | None:
        return PlainTextSearchQuery

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
        content: "PlainTextContent",
    ) -> dict[str, Any] | None:
        return content.model_dump(include={"text"})

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "PlainTextSearchQuery",
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
        contents: list["PlainTextContent"],
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
        resource: "PlainTextResource",
        contents: list["PlainTextContent"],
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
                    "TEXT",
                    "AUTHORS_COMMENT",
                    "EDITORS_COMMENT",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_loc_labels.get(str(content.location_id), ""),
                        sort_num,
                        content.text,
                        content.authors_comment,
                        content.editors_comment,
                    ]
                )
                sort_num += 1


class FocusViewConfig(ModelBase):
    single_line: Annotated[
        bool,
        Field(
            description="Show contents as single line of text when in focus view",
        ),
    ] = True
    delimiter: Annotated[
        ConStr(
            min_length=1,
            max_length=3,
            strip=False,
            pattern=r"[^\n\r]+",
        ),
        Field(
            description=("Delimiter used for single-line display in focus view"),
        ),
    ] = " / "


class LineLabellingConfig(ModelBase):
    enabled: Annotated[
        bool,
        Field(
            description="Enable/disable line labelling",
        ),
    ] = False
    labelling_type: Annotated[
        Literal[
            "numbersZeroBased",
            "numbersOneBased",
            "lettersLowercase",
            "lettersUppercase",
        ],
        Field(
            description="Line labelling type",
        ),
    ] = "numbersOneBased"


type DeepLSourceLanguage = Literal[
    "ar",
    "bg",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fi",
    "fr",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "lt",
    "lv",
    "nb",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sv",
    "tr",
    "uk",
    "zh",
]


class DeepLLinksConfig(ModelBase):
    """
    Resource configuration model for DeepL translation links.
    The corresponding field MUST be named `deepl_links`!
    """

    enabled: Annotated[
        bool,
        Field(
            description="Enable/disable quick translation links to DeepL",
        ),
    ] = False
    source_language: Annotated[
        DeepLSourceLanguage | None,
        Field(
            description="Source language",
        ),
    ] = None


class PlainTextSpecialConfig(ModelBase):
    """Config properties specific to the plain text resource type"""

    # generic special config items
    search_replacements: SearchReplacements = []
    content_css: ContentCssProperties = []

    # resource type-specific config items
    focus_view: FocusViewConfig = FocusViewConfig()
    line_labelling: LineLabellingConfig = LineLabellingConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlainTextResourceConfig(ResourceConfigBase):
    special: PlainTextSpecialConfig = PlainTextSpecialConfig()


class PlainTextResource(ResourceBase):
    resource_type: Literal["plainText"]  # camelCased resource type classname
    config: PlainTextResourceConfig = PlainTextResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["text"]


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        ConStr(
            max_length=102400,
            cleanup="multiline",
        ),
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
        ConStr(
            min_length=0,
            max_length=512,
            cleanup="oneline",
        ),
        Field(
            description="Text content search query",
        ),
        SchemaOptionalNullable,
    ] = ""
