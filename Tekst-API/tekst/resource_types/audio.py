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


class Audio(ResourceTypeBase):
    """A resource type for audio files"""

    @classmethod
    def resource_model(cls) -> type["AudioResource"]:
        return AudioResource

    @classmethod
    def content_model(cls) -> type["AudioContent"]:
        return AudioContent

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
        assert isinstance(query.resource_type_specific, AudioSearchQuery)
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
        resource: "AudioResource",
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
                    "CAPTION",
                    "COMMENTS",
                ]
            )
            async for content in ContentBaseDocument.find(
                In(ContentBaseDocument.id, content_ids),
                with_children=True,
            ):
                for audio_file in content.files:
                    csv_writer.writerow(
                        [
                            full_loc_labels.get(str(content.location_id), ""),
                            sort_num,
                            audio_file.url,
                            audio_file.caption,
                            content.comments_for_csv(),
                        ]
                    )
                    sort_num += 1


class AudioResourceConfig(ResourceConfigBase):
    pass


class AudioResource(ResourceBase):
    resource_type: Literal["audio"]  # camelCased resource type classname
    config: AudioResourceConfig = AudioResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["caption"]

    @classmethod
    def create_model(cls):
        return AudioResourceCreate

    @classmethod
    def read_model(cls):
        return AudioResourceRead

    @classmethod
    def update_model(cls):
        return AudioResourceUpdate

    @classmethod
    def document_model(cls):
        return AudioResourceDocument


class AudioResourceCreate(AudioResource, CreateBase):
    pass


class AudioResourceRead(AudioResource, ResourceReadExtras, ReadBase):
    pass


AudioResourceUpdate = make_update_model(AudioResource)


class AudioResourceDocument(AudioResource, ResourceBaseDocument):
    pass


class AudioFile(ModelBase):
    url: Annotated[
        HttpUrl,
        Field(description="URL of the audio file"),
    ]
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
        Field(description="Caption of the audio file"),
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

    @classmethod
    def create_model(cls):
        return AudioContentCreate

    @classmethod
    def read_model(cls):
        return AudioContentRead

    @classmethod
    def update_model(cls):
        return AudioContentUpdate

    @classmethod
    def document_model(cls):
        return AudioContentDocument


class AudioContentCreate(AudioContent, CreateBase):
    pass


class AudioContentRead(AudioContent, ReadBase):
    pass


AudioContentUpdate = make_update_model(AudioContent)


class AudioContentDocument(AudioContent, ContentBaseDocument):
    pass


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
        StringConstraints(max_length=512),
        SingleLineString,
        SchemaOptionalNullable,
    ] = ""
