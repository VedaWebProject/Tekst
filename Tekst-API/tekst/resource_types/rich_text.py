import csv

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from beanie import PydanticObjectId
from beanie.operators import In
from pydantic import Field, StringConstraints, field_validator

from tekst.html import get_html_text, sanitize_html
from tekst.models.common import CreateBase, ModelBase, ReadBase, make_update_model
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
    ResourceReadExtras,
)
from tekst.models.resource_configs import (
    GeneralResourceConfig,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceTypeBase
from tekst.types import (
    CollapsibleContentsConfigValue,
    ContentCssProperties,
    ExcludeFromModelVariants,
    SchemaOptionalNonNullable,
    SchemaOptionalNullable,
    SearchReplacements,
    SingleLineString,
)
from tekst.utils import ensure


if TYPE_CHECKING:
    from tekst.models.search import ResourceSearchQuery


class RichText(ResourceTypeBase):
    """A simple rich text resource type"""

    @classmethod
    def resource_model(cls) -> type["RichTextResource"]:
        return RichTextResource

    @classmethod
    def content_model(cls) -> type["RichTextContent"]:
        return RichTextContent

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
        content: ContentBase,
    ) -> dict[str, Any] | None:
        if not isinstance(content, RichTextContent):  # pragma: no cover
            raise ValueError(f"Expected RichTextContent, got {type(content)}")
        return {"html": get_html_text(content.html)}

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        assert isinstance(query.resource_type_specific, RichTextSearchQuery)
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
        resource: "RichTextResource",
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
            csv_writer.writerow(
                [
                    "LOCATION",
                    "SORT",
                    "HTML",
                    "COMMENTS",
                ]
            )
            async for content in ContentBaseDocument.find(
                In(ContentBaseDocument.id, content_ids),
                with_children=True,
            ):
                csv_writer.writerow(
                    [
                        full_loc_labels.get(str(content.location_id), ""),
                        sort_num,
                        content.html,
                        content.comments_for_csv(),
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

    @classmethod
    def create_model(cls):
        return RichTextResourceCreate

    @classmethod
    def read_model(cls):
        return RichTextResourceRead

    @classmethod
    def update_model(cls):
        return RichTextResourceUpdate

    @classmethod
    def document_model(cls):
        return RichTextResourceDocument


class RichTextResourceCreate(RichTextResource, CreateBase):
    pass


class RichTextResourceRead(RichTextResource, ResourceReadExtras, ReadBase):
    pass


RichTextResourceUpdate = make_update_model(RichTextResource)


class RichTextResourceDocument(RichTextResource, ResourceBaseDocument):
    pass


class RichTextContent(ContentBase):
    """A content of a rich text resource"""

    resource_type: Literal["richText"]  # camelCased resource type classname
    html: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400),
        Field(description="HTML content of the rich text content object"),
    ]
    editor_mode: Annotated[
        Literal["wysiwyg", "html"],
        Field(description="Last used editor mode for this content"),
    ] = "wysiwyg"

    @field_validator("html", mode="after")
    @classmethod
    def validate_html(cls, value) -> str:
        return sanitize_html(value) or ""

    @classmethod
    def create_model(cls):
        return RichTextContentCreate

    @classmethod
    def read_model(cls):
        return RichTextContentRead

    @classmethod
    def update_model(cls):
        return RichTextContentUpdate

    @classmethod
    def document_model(cls):
        return RichTextContentDocument


class RichTextContentCreate(RichTextContent, CreateBase):
    pass


class RichTextContentRead(RichTextContent, ReadBase):
    pass


RichTextContentUpdate = make_update_model(RichTextContent)


class RichTextContentDocument(RichTextContent, ContentBaseDocument):
    pass


class RichTextSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["richText"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    html: Annotated[
        str,
        StringConstraints(min_length=1, max_length=512),
        SingleLineString,
        Field(description="HTML text content search query"),
        SchemaOptionalNullable,
    ] = ""
