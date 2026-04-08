import csv

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import AfterValidator, Field, StringConstraints

from tekst.models.common import CreateBase, ModelBase, ReadBase, make_update_model
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
    ResourceReadExtras,
)
from tekst.models.resource_configs import ResourceConfigBase
from tekst.models.text import TextDocument
from tekst.resources import ResourceTypeBase
from tekst.types import (
    ContentCssProperties,
    FalsyToNone,
    MultiLineString,
    SchemaOptionalNullable,
    SearchReplacements,
    SingleLineString,
)


if TYPE_CHECKING:
    from tekst.models.search import ResourceSearchQuery


class PlainText(ResourceTypeBase):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent

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
        content: ContentBase,
    ) -> dict[str, Any] | None:
        return content.model_dump(include={"text"})

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        assert isinstance(query.resource_type_specific, PlainTextSearchQuery)
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
        contents: list[ContentBaseDocument],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        if export_format == "csv":
            await cls._export_csv(resource, contents, file_path)  # ty:ignore[invalid-argument-type]
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
        if not text:  # pragma: no cover
            raise ValueError(f"Text with ID '{resource.text_id}' not found")
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
                    "COMMENTS",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_loc_labels.get(str(content.location_id), ""),
                        sort_num,
                        content.text,
                        await content.comments_for_csv(),
                    ]
                )
                sort_num += 1


class FocusViewConfig(ModelBase):
    single_line: Annotated[
        bool,
        Field(description="Show contents as single line of text when in focus view"),
    ] = True
    delimiter: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=3,
            strip_whitespace=False,
            pattern=r"[^\n\r]+",
        ),
        Field(description="Delimiter used for single-line display in focus view"),
    ] = " / "


class LineLabellingConfig(ModelBase):
    enabled: Annotated[
        bool,
        Field(description="Enable/disable line labelling"),
    ] = False
    labelling_type: Annotated[
        Literal[
            "numbersZeroBased",
            "numbersOneBased",
            "lettersLowercase",
            "lettersUppercase",
        ],
        Field(description="Line labelling type"),
    ] = "numbersOneBased"


class DeepLLinksConfig(ModelBase):
    """
    Resource configuration model for DeepL translation links.
    The corresponding field MUST be named `deepl_links`!
    """

    enabled: Annotated[
        bool,
        Field(description="Enable/disable quick translation links to DeepL"),
    ] = False
    source_language: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=16),
        SingleLineString,
        FalsyToNone,
        Field(description="DeepL source language code"),
        AfterValidator(lambda x: x.lower() if x else None),
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

    @classmethod
    def create_model(cls):
        return PlainTextResourceCreate

    @classmethod
    def read_model(cls):
        return PlainTextResourceRead

    @classmethod
    def update_model(cls):
        return PlainTextResourceUpdate

    @classmethod
    def document_model(cls):
        return PlainTextResourceDocument


class PlainTextResourceCreate(PlainTextResource, CreateBase):
    pass


class PlainTextResourceRead(PlainTextResource, ResourceReadExtras, ReadBase):
    pass


PlainTextResourceUpdate = make_update_model(PlainTextResource)


class PlainTextResourceDocument(PlainTextResource, ResourceBaseDocument):
    pass


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400),
        MultiLineString,
        Field(description="Text content of the plain text content object"),
    ]

    @classmethod
    def create_model(cls):
        return PlainTextContentCreate

    @classmethod
    def read_model(cls):
        return PlainTextContentRead

    @classmethod
    def update_model(cls):
        return PlainTextContentUpdate

    @classmethod
    def document_model(cls):
        return PlainTextContentDocument


class PlainTextContentCreate(PlainTextContent, CreateBase):
    pass


class PlainTextContentRead(PlainTextContent, ReadBase):
    pass


PlainTextContentUpdate = make_update_model(PlainTextContent)


class PlainTextContentDocument(PlainTextContent, ContentBaseDocument):
    pass


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
        StringConstraints(max_length=512),
        SingleLineString,
        Field(description="Text content search query"),
        SchemaOptionalNullable,
    ] = ""
