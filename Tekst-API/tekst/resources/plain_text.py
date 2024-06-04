import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ReducedViewOnelineConfigType,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.utils import validators as val


class PlainText(ResourceTypeABC):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent

    @classmethod
    def search_query_model(cls) -> type["PlainTextSearchQuery"]:
        return PlainTextSearchQuery

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "text": {
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {"strict": {"type": "text"}},
            },
        }

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "PlainTextContent",
    ) -> dict[str, Any]:
        return content.model_dump(include={"text"})

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""

        if not query.resource_type_specific.text.strip("*"):
            # handle empty/match-all query (query for existing target field)
            es_queries.append(
                {
                    "exists": {
                        "field": f"resources.{query.common.resource_id}",
                    }
                }
            )
        else:
            # handle actual query with content
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            f"resources.{query.common.resource_id}.text{strict_suffix}"
                        ],
                        "query": query.resource_type_specific.text,
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
        else:
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
            csv_writer.writerow(["LOCATION", "TEXT", "COMMENT"])
            for content in contents:
                csv_writer.writerow(
                    [
                        full_location_labels.get(str(content.location_id), ""),
                        content.text,
                        content.comment,
                    ]
                )


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


class DeepLLinksConfig(ModelBase):
    """
    Resource configuration model for DeepL translation links.
    The corresponding field MUST be named `deepl_links`!
    """

    _DEEPL_LANGUAGES: tuple = (
        "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI",
        "FR", "HU", "ID", "IT", "JA", "LT", "LV", "NL", "PL",
        "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH",
    )  # fmt: skip

    enabled: Annotated[
        bool,
        Field(
            description="Enable/disable quick translation links to DeepL",
        ),
    ] = False
    source_language: Annotated[
        Literal[_DEEPL_LANGUAGES] | None,
        Field(
            description="Source language",
        ),
    ] = _DEEPL_LANGUAGES[0]
    languages: Annotated[
        list[Literal[_DEEPL_LANGUAGES]],
        Field(
            description="Target languages to display links for",
            max_length=32,
        ),
    ] = ["EN", "DE"]


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    reduced_view_oneline: ReducedViewOnelineConfigType = False
    font: FontConfigType = None


class PlainTextResourceConfig(ResourceConfigBase):
    general: GeneralPlainTextResourceConfig = GeneralPlainTextResourceConfig()
    line_labelling: LineLabellingConfig = LineLabellingConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlainTextResource(ResourceBase):
    resource_type: Literal["plainText"]  # camelCased resource type classname
    config: PlainTextResourceConfig = PlainTextResourceConfig()


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=102400,
            strip_whitespace=True,
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
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
    ] = ""
