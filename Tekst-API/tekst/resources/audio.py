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


class Audio(ResourceTypeABC):
    """A resource type for audio files"""

    @classmethod
    def resource_model(cls) -> type["AudioResource"]:
        return AudioResource

    @classmethod
    def content_model(cls) -> type["AudioContent"]:
        return AudioContent

    @classmethod
    def search_query_model(cls) -> type["AudioSearchQuery"]:
        return AudioSearchQuery

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "caption": {
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {"strict": {"type": "text"}},
                "index_prefixes": {},
            },
        }

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "AudioContent",
    ) -> dict[str, Any]:
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
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]]:
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
        contents: list["AudioContent"],
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
        resource: "AudioResource",
        contents: list["AudioContent"],
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
                    "CAPTION",
                    "LOCATION_COMMENT",
                ]
            )
            for content in contents:
                for audio_file in content.files:
                    csv_writer.writerow(
                        [
                            full_location_labels.get(str(content.location_id), ""),
                            audio_file.url,
                            audio_file.caption,
                            content.comment,
                        ]
                    )


class GeneralAudioResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType = None


class AudioResourceConfig(ResourceConfigBase):
    general: GeneralAudioResourceConfig = GeneralAudioResourceConfig()


class AudioResource(ResourceBase):
    resource_type: Literal["audio"]  # camelCased resource type classname
    config: AudioResourceConfig = AudioResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["caption"]


class AudioFile(ModelBase):
    url: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=2083,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
        Field(
            description="URL of the audio file",
        ),
    ]
    source_url: Annotated[
        str | None,
        StringConstraints(
            max_length=2083,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
        Field(
            description="URL of the source website of the image",
        ),
    ] = None
    caption: Annotated[
        str | None,
        StringConstraints(
            max_length=8192,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
        Field(
            description="Caption of the audio file",
        ),
    ] = None


class AudioContent(ContentBase):
    """A content of an audio resource"""

    resource_type: Literal["audio"]  # camelCased resource type classname
    files: Annotated[
        list[AudioFile],
        Field(
            description="List of audio file objects",
            min_length=1,
            max_length=100,
        ),
    ]


class AudioSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["audio"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    caption: Annotated[
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
        SchemaOptionalNonNullable,
    ] = ""
