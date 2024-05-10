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
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.utils import validators as val


class Images(ResourceTypeABC):
    """A resource type for image files"""

    @classmethod
    def resource_model(cls) -> type["ImagesResource"]:
        return ImagesResource

    @classmethod
    def content_model(cls) -> type["ImagesContent"]:
        return ImagesContent

    @classmethod
    def search_query_model(cls) -> type["ImagesSearchQuery"]:
        return ImagesSearchQuery

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "caption": {
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {"strict": {"type": "text"}},
            },
        }

    @classmethod
    def rtype_index_doc_data(cls, content: "ImagesContent") -> dict[str, Any]:
        return {
            "caption": [
                f.get("caption", "")
                for f in content.model_dump(include={"files"}).get("files", [])
            ]
        }

    @classmethod
    def rtype_es_queries(
        cls, *, query: ResourceSearchQuery, strict: bool = False
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""

        if not query.resource_type_specific.caption.strip("*"):
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
                            f"resources.{query.common.resource_id}.caption{strict_suffix}"
                        ],
                        "query": query.resource_type_specific.caption,
                    }
                }
            )
        return es_queries

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list["ImagesContent"],
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
        resource: "ImagesResource",
        contents: list["ImagesContent"],
        file_path: Path,
    ) -> None:
        text = await TextDocument.get(resource.text_id)
        # construct labels of all locations on the resource's level
        full_location_labels = await text.full_location_labels(resource.level)
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile, dialect="excel", quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["LOCATION", "URL", "THUMB_URL", "CAPTION", "COMMENT"])
            for content in contents:
                for image_file in content.files:
                    csv_writer.writerow(
                        [
                            full_location_labels.get(str(content.location_id), ""),
                            image_file.url,
                            image_file.thumb_url,
                            image_file.caption,
                            content.comment,
                        ]
                    )


class GeneralImagesResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = True
    font: FontConfigType | None = None


class ImagesResourceConfig(ResourceConfigBase):
    general: GeneralImagesResourceConfig = GeneralImagesResourceConfig()


class ImagesResource(ResourceBase):
    resource_type: Literal["images"]  # camelCased resource type classname
    config: ImagesResourceConfig = ImagesResourceConfig()


class ImageFile(ModelBase):
    url: Annotated[
        str,
        StringConstraints(min_length=1, max_length=2083, strip_whitespace=True),
        val.CleanupOneline,
        Field(
            description="URL of the image file",
        ),
    ]
    thumb_url: Annotated[
        str | None,
        StringConstraints(max_length=2083, strip_whitespace=True),
        val.CleanupOneline,
        Field(
            description="URL of the image file thumbnail",
        ),
    ] = None
    caption: Annotated[
        str | None,
        StringConstraints(max_length=8192, strip_whitespace=True),
        val.CleanupMultiline,
        Field(
            description="Caption of the image",
        ),
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
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = ""
