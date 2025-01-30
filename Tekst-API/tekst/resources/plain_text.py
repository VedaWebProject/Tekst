import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field
from typing_extensions import TypeAliasType

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
    DefaultCollapsedValue,
    FontNameValueOrNone,
    SchemaOptionalNullable,
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
    def rtype_index_doc_props(cls) -> dict[str, Any] | None:
        return {
            "text": {
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {
                    "strict": {
                        "type": "text",
                    }
                },
                "index_prefixes": {},
            },
        }

    @classmethod
    def rtype_index_doc_data(
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
                    "TEXT",
                    "LOCATION_COMMENT",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_location_labels.get(str(content.location_id), ""),
                        content.text,
                        content.comment,
                    ]
                )


class ReducedViewConfig(ModelBase):
    single_line: Annotated[
        bool,
        Field(
            description="Show contents as single line of text when in reduced view",
        ),
    ]
    single_line_delimiter: Annotated[
        ConStr(
            min_length=1,
            max_length=3,
            strip=False,
            pattern=r"[^\n\r]+",
        ),
        Field(
            description=(
                "Delimiter used for single-line display in reduced reading mode"
            ),
        ),
    ]


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


DeepLSourceLanguage = TypeAliasType(
    "DeepLSourceLanguage",
    Literal[
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
    ],
)


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


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedValue = False
    font: FontNameValueOrNone = None
    reduced_view: ReducedViewConfig = ReducedViewConfig(
        single_line=False,
        single_line_delimiter=" / ",
    )


class PlainTextResourceConfig(ResourceConfigBase):
    general: GeneralPlainTextResourceConfig = GeneralPlainTextResourceConfig()
    line_labelling: LineLabellingConfig = LineLabellingConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


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
