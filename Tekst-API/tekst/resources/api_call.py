import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field

from tekst.models.common import CustomHttpUrl, ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    CommonResourceConfig,
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC


class ApiCall(ResourceTypeABC):
    """A resource type for calls to an API"""

    @classmethod
    def resource_model(cls) -> type["ApiCallResource"]:
        return ApiCallResource

    @classmethod
    def content_model(cls) -> type["ApiCallContent"]:
        return ApiCallContent

    @classmethod
    def search_query_model(cls) -> type[ResourceSearchQuery] | None:
        return None  # pragma: no cover

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any] | None:
        return None  # pragma: no cover

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "ApiCallContent",
    ) -> dict[str, Any] | None:
        return None  # pragma: no cover

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        return None  # pragma: no cover

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list["ApiCallContent"],
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
        resource: "ApiCallResource",
        contents: list["ApiCallContent"],
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
                    "LOCATION_COMMENT",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_location_labels.get(str(content.location_id), ""),
                        content.url,
                        content.comment,
                    ]
                )


class GeneralApiCallResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType = None


class ApiCallResourceConfig(ResourceConfigBase):
    # overriding common resource config field of ResourceConfigBase
    # to default quick_searchable to False
    common: CommonResourceConfig = CommonResourceConfig(quick_searchable=False)
    general: GeneralApiCallResourceConfig = GeneralApiCallResourceConfig()


class ApiCallResource(ResourceBase):
    resource_type: Literal["apiCall"]  # camelCased resource type classname
    config: ApiCallResourceConfig = ApiCallResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return []  # pragma: no cover


class ApiCallContent(ContentBase):
    """A content of an API call resource"""

    resource_type: Literal["apiCall"]  # camelCased resource type classname
    url: Annotated[
        CustomHttpUrl,
        Field(
            description="URL to use for the HTTP (GET) call",
        ),
    ]
