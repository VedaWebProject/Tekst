from collections.abc import Callable
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, conint, field_validator
from typing_extensions import TypeAliasType

from tekst.models.common import (
    ModelBase,
    PydanticObjectId,
    SchemaOptionalNonNullable,
    SchemaOptionalNullable,
)
from tekst.resources import ResourceSearchQuery


class SearchHit(ModelBase):
    id: PydanticObjectId
    label: str
    full_label: str
    text_id: PydanticObjectId
    level: int
    position: int
    score: float | None
    highlight: dict[str, list[str]] = {}


class SearchResults(ModelBase):
    hits: list[SearchHit]
    took: int
    total_hits: int
    total_hits_relation: Literal["eq", "gte"]
    max_score: float | None

    @classmethod
    def __transform_highlights(
        cls,
        hit: dict[str, Any],
        highlights_generators: dict[str, Callable[[dict[str, Any]], list[str]]],
    ) -> dict[str, set[str]]:
        if not hit.get("highlight"):
            return {}
        highlights = {}
        highlights_generators = highlights_generators or {}
        for k, v in hit["highlight"].items():
            hl_res_id = k.split(".")[1]
            if hl_res_id not in highlights:
                highlights[hl_res_id] = set()
            if hl_res_id in highlights_generators:
                v = highlights_generators[hl_res_id](hit)
            highlights[hl_res_id].update(v)
        return highlights

    @classmethod
    def from_es_results(
        cls,
        results: dict[str, Any],
        highlights_generators: dict[str, Callable[[dict[str, Any]], list[str]]]
        | None = None,
    ) -> "SearchResults":
        return cls(
            hits=[
                SearchHit(
                    id=hit["_id"],
                    label=hit["_source"]["label"],
                    full_label=hit["_source"]["full_label"],
                    text_id=hit["_source"]["text_id"],
                    level=hit["_source"]["level"],
                    position=hit["_source"]["position"],
                    score=hit["_score"],
                    highlight=cls.__transform_highlights(
                        hit, highlights_generators or {}
                    ),
                )
                for hit in results["hits"]["hits"]
            ],
            took=results["took"],
            total_hits=results["hits"]["total"]["value"],
            total_hits_relation=results["hits"]["total"]["relation"],
            max_score=results["hits"]["max_score"],
        )


SortingPreset = TypeAliasType(
    "SortingPreset", Literal["relevance", "text_level_position", "text_level_relevance"]
)


class PaginationSettings(ModelBase):
    page: Annotated[
        int,
        conint(
            ge=1,
        ),
        Field(
            alias="pg",
            description="Page number",
        ),
        SchemaOptionalNonNullable,
    ] = 1
    page_size: Annotated[
        int,
        Literal[10, 25, 50],
        Field(
            alias="pgs",
            description="Page size",
        ),
        SchemaOptionalNonNullable,
    ] = 10

    def es_from(self) -> int:
        return (self.page - 1) * self.page_size

    def es_size(self) -> int:
        return self.page_size

    def mongo_skip(self) -> int:
        return (self.page - 1) * self.page_size if self.page > 0 else 0

    def mongo_limit(self) -> int:
        return self.page_size


class GeneralSearchSettings(ModelBase):
    pagination: Annotated[
        PaginationSettings,
        Field(
            alias="pgn",
            description="Pagination settings",
        ),
        SchemaOptionalNonNullable,
    ] = PaginationSettings()
    sorting_preset: Annotated[
        SortingPreset | None,
        Field(
            alias="sort",
            description="Sorting preset",
        ),
        SchemaOptionalNullable,
    ] = None
    strict: bool = False


class QuickSearchSettings(ModelBase):
    default_operator: Annotated[
        Literal["AND", "OR"],
        Field(
            alias="op",
            description="Default operator",
        ),
        SchemaOptionalNonNullable,
    ] = "OR"
    regexp: Annotated[
        bool,
        Field(
            alias="re",
            description="Whether to use regular expressions",
        ),
        SchemaOptionalNonNullable,
    ] = False
    texts: Annotated[
        list[PydanticObjectId] | None,
        Field(
            alias="txt",
            description="IDs of texts to search in",
        ),
        SchemaOptionalNullable,
    ] = None

    @field_validator(
        "default_operator",
        mode="before",
    )
    @classmethod
    def default_operator_upper(cls, v: Any) -> str:
        return str(v).upper()


class AdvancedSearchSettings(ModelBase):
    pass


class QuickSearchRequestBody(ModelBase):
    search_type: Annotated[
        Literal["quick"],
        Field(
            alias="type",
            description="Search type",
        ),
    ] = "quick"
    query: Annotated[
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        Field(
            alias="q",
            description="Query string",
        ),
        SchemaOptionalNonNullable,
    ] = "*"
    settings_general: Annotated[
        GeneralSearchSettings,
        Field(
            alias="gen",
            description="General search settings",
        ),
        SchemaOptionalNonNullable,
    ] = GeneralSearchSettings()
    settings_quick: Annotated[
        QuickSearchSettings,
        Field(
            alias="qck",
            description="Quick search settings",
        ),
        SchemaOptionalNonNullable,
    ] = QuickSearchSettings()


class AdvancedSearchRequestBody(ModelBase):
    search_type: Annotated[
        Literal["advanced"],
        Field(
            alias="type",
            description="Search type",
        ),
    ] = "advanced"
    queries: Annotated[
        list[ResourceSearchQuery],
        Field(
            alias="q",
            max_length=32,
            description="Resource-specific queries",
        ),
        SchemaOptionalNonNullable,
    ] = []
    settings_general: Annotated[
        GeneralSearchSettings,
        Field(
            alias="gen",
            description="General search settings",
        ),
        SchemaOptionalNonNullable,
    ] = GeneralSearchSettings()
    settings_advanced: Annotated[
        AdvancedSearchSettings,
        Field(
            alias="adv",
            description="Advanced search settings",
        ),
        SchemaOptionalNonNullable,
    ] = AdvancedSearchSettings()


class IndexInfo(ModelBase):
    text_id: PydanticObjectId | None
    documents: int
    size: str
    searches: int
    fields: int
    up_to_date: bool
