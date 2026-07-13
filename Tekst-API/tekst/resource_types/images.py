import csv

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from beanie import PydanticObjectId
from beanie.operators import In
from pydantic import Field, StringConstraints

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
    FalsyToNone,
    HttpUrl,
    MultiLineString,
    SchemaOptionalNullable,
    SingleLineString,
)
from tekst.utils import ensure


if TYPE_CHECKING:
    from tekst.models.search import ResourceSearchQuery


class Images(ResourceTypeBase):
    """A resource type for image files"""

    @classmethod
    def resource_model(cls) -> type["ImagesResource"]:
        return ImagesResource

    @classmethod
    def content_model(cls) -> type["ImagesContent"]:
        return ImagesContent

    @classmethod
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        return {
            "caption": {
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
        return {
            "caption": [
                f.get("caption", "")
                for f in content.model_dump(include={"files"}).get("files", [])
            ]
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        assert isinstance(query.resource_type_specific, ImagesSearchQuery)
        es_queries = []

        # add query only if not "empty"
        if query.resource_type_specific.caption.strip("* "):
            strict_suffix = ".strict" if strict else ""
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            f"resources.{str(query.common.resource_id)}.caption{strict_suffix}"
                        ],
                        "query": query.resource_type_specific.caption,
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
        resource: "ImagesResource",
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
                    "URL",
                    "THUMB_URL",
                    "CAPTION",
                    "COMMENTS",
                ]
            )
            async for content in ContentBaseDocument.find(
                In(ContentBaseDocument.id, content_ids),
                with_children=True,
            ):
                for image_file in content.files:
                    csv_writer.writerow(
                        [
                            full_loc_labels.get(str(content.location_id), ""),
                            sort_num,
                            image_file.url,
                            image_file.thumb_url,
                            image_file.caption,
                            content.comments_for_csv(),
                        ]
                    )
                    sort_num += 1


class ImagesResourceConfig(ResourceConfigBase):
    pass


class ImagesResource(ResourceBase):
    resource_type: Literal["images"]  # camelCased resource type classname
    config: ImagesResourceConfig = ImagesResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["caption"]

    @classmethod
    def create_model(cls):
        return ImagesResourceCreate

    @classmethod
    def read_model(cls):
        return ImagesResourceRead

    @classmethod
    def update_model(cls):
        return ImagesResourceUpdate

    @classmethod
    def document_model(cls):
        return ImagesResourceDocument


class ImagesResourceCreate(ImagesResource, CreateBase):
    pass


class ImagesResourceRead(ImagesResource, ResourceReadExtras, ReadBase):
    pass


ImagesResourceUpdate = make_update_model(ImagesResource)


class ImagesResourceDocument(ImagesResource, ResourceBaseDocument):
    pass


class ImageFile(ModelBase):
    url: Annotated[
        HttpUrl,
        Field(description="URL of the image file"),
    ]
    thumb_url: Annotated[
        HttpUrl | None,
        FalsyToNone,
        Field(description="URL of the image file thumbnail"),
    ] = None
    source_url: Annotated[
        HttpUrl | None,
        FalsyToNone,
        Field(description="URL of the source website of the image"),
    ] = None
    caption: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=8192),
        MultiLineString,
        FalsyToNone,
        Field(description="Caption of the image"),
    ] = None


class ImagesContent(ContentBase):
    """A content of an images resource"""

    resource_type: Literal["images"]  # camelCased resource type classname
    files: Annotated[
        list[ImageFile],
        Field(
            description="List of image file objects",
            min_length=1,
            max_length=100,
        ),
    ]

    @classmethod
    def create_model(cls):
        return ImagesContentCreate

    @classmethod
    def read_model(cls):
        return ImagesContentRead

    @classmethod
    def update_model(cls):
        return ImagesContentUpdate

    @classmethod
    def document_model(cls):
        return ImagesContentDocument


class ImagesContentCreate(ImagesContent, CreateBase):
    pass


class ImagesContentRead(ImagesContent, ReadBase):
    pass


ImagesContentUpdate = make_update_model(ImagesContent)


class ImagesContentDocument(ImagesContent, ContentBaseDocument):
    pass


class ImagesSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["images"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    caption: Annotated[
        str,
        StringConstraints(max_length=512),
        SingleLineString,
        Field(description="Caption content search query"),
        SchemaOptionalNullable,
    ] = ""
