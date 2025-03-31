import csv

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    GeneralResourceConfig,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceSearchQuery, ResourceTypeABC
from tekst.types import (
    ConStr,
    ConStrOrNone,
    ExcludeFromModelVariants,
    HttpUrl,
    SchemaOptionalNonNullable,
)


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
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        return None  # pragma: no cover

    @classmethod
    def _rtype_index_doc(
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
                    "ENDPOINT",
                    "METHOD",
                    "CONTENT_TYPE",
                    "QUERY",
                    "LOCATION_COMMENT",
                ]
            )
            for content in contents:
                csv_writer.writerow(
                    [
                        full_location_labels.get(str(content.location_id), ""),
                        resource.config.special.api_call.endpoint,
                        resource.config.special.api_call.method,
                        resource.config.special.api_call.content_type,
                        content.query,
                        content.comment,
                    ]
                )


class ApiCallModGeneralConfig(GeneralResourceConfig):
    enable_content_context: Annotated[
        Literal[False],
        Field(
            description=(
                "Whether contents of this resource should be available for the parent "
                "level (always false for API call resources)"
            ),
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
        SchemaOptionalNonNullable,
    ] = False
    searchable_quick: Annotated[
        Literal[False],
        Field(
            description=(
                "Whether this resource should be included in quick search "
                "(always false as API call contents are not searchable)"
            ),
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
        SchemaOptionalNonNullable,
    ] = False
    searchable_adv: Annotated[
        Literal[False],
        Field(
            description=(
                "Whether this resource should accessible via advanced search "
                "(always false as API call contents are not searchable)"
            ),
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
        SchemaOptionalNonNullable,
    ] = False


class ApiCallConfig(ModelBase):
    endpoint: HttpUrl = "https://api.example.com/v2/some/endpoint"
    method: Literal["GET", "POST", "QUERY", "SEARCH"] = "GET"
    content_type: ConStr(
        max_length=64,
    ) = "application/json"


class ContentTransformConfig(ModelBase):
    deps: Annotated[
        list[HttpUrl],
        Field(
            min_length=0,
            max_length=32,
        ),
    ] = []
    js: Annotated[
        ConStrOrNone(
            min_length=0,
            max_length=102400,
        ),
        SchemaOptionalNonNullable,
    ] = None

    @model_validator(mode="after")
    def validate_config(self):
        if self.deps and not self.js:  # pragma: no cover
            self.deps = []
        return self


class ApiCallSpecialConfig(ModelBase):
    api_call: ApiCallConfig = ApiCallConfig()
    transform: ContentTransformConfig = ContentTransformConfig()


class ApiCallResourceConfig(ResourceConfigBase):
    # override common resource config field of ResourceConfigBase
    general: ApiCallModGeneralConfig = ApiCallModGeneralConfig()
    special: ApiCallSpecialConfig = ApiCallSpecialConfig()


class ApiCallResource(ResourceBase):
    resource_type: Literal["apiCall"]  # camelCased resource type classname
    config: ApiCallResourceConfig = ApiCallResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return []  # pragma: no cover


class ApiCallContent(ContentBase):
    """A content of an API call resource"""

    resource_type: Literal["apiCall"]  # camelCased resource type classname
    query: Annotated[
        ConStr(
            max_length=102400,
        ),
        Field(
            description=(
                "Query payload to use for the API call. This can be a URL query string,"
                "(for GET requests) a JSON object, or whatever the API expects."
            ),
        ),
    ]
    transform_context: Annotated[
        ConStrOrNone(
            max_length=10240,
        ),
        Field(
            description=(
                "Extra data that will be made available to the transformation script. "
                "This has to be a valid, string-encoded JSON object."
            ),
        ),
        SchemaOptionalNonNullable,
    ] = None
