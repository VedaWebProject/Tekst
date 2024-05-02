import json

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
    DeepLLinksConfig,
    DefaultCollapsedConfigType,
    FontConfigType,
    ReducedViewOnelineConfigType,
    ResourceConfigBase,
)
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
    def rtype_index_doc_data(cls, content: "PlainTextContent") -> dict[str, Any]:
        return content.model_dump(include={"text"})

    @classmethod
    def rtype_es_queries(
        cls, *, query: ResourceSearchQuery, strict: bool = False
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
    ) -> str:
        if export_format not in {"json"}:
            raise ValueError(
                f"Unsupported export format '{export_format}' "
                f"for resource type '{cls.get_key()}'"
            )
        contents = [
            c.model_dump(
                by_alias=True,
                exclude_unset=True,
                exclude=cls._EXCLUDE_FROM_CONTENT_EXPORT_DATA,
            )
            for c in contents
        ]
        return json.dumps(contents, indent=2, ensure_ascii=False)


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    reduced_view_oneline: ReducedViewOnelineConfigType = False
    font: FontConfigType | None = None


class PlainTextResourceConfig(ResourceConfigBase):
    general: GeneralPlainTextResourceConfig = GeneralPlainTextResourceConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlainTextResource(ResourceBase):
    resource_type: Literal["plainText"]  # camelCased resource type classname
    config: PlainTextResourceConfig = PlainTextResourceConfig()


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400, strip_whitespace=True),
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
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = ""
