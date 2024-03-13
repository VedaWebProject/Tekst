from datetime import datetime
from typing import Annotated, Any, Literal, Union

from fastapi import Body
from pydantic import Field, StringConstraints, conint, field_validator
from typing_extensions import TypeAliasType

from tekst.models.common import ModelBase, PydanticObjectId
from tekst.resources import AnyResourceSearchQuery


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
    index_creation_time: datetime

    @classmethod
    def __transform_highlights(cls, hit: dict[str, Any]) -> dict[str, list[str]]:
        if not hit.get("highlight"):
            return {}
        highlights = {}
        for k, v in hit["highlight"].items():
            try:
                res_id = k.split(".")[0]
                hl_key = hit["_source"][res_id]["resource_title"]
                if hl_key not in highlights:
                    highlights[hl_key] = set()
                highlights[hl_key].update(v)
            except Exception:
                highlights[k] = v
        return highlights

    @classmethod
    def from_es_results(
        cls, results: dict[str, Any], index_creation_time: datetime
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
                    highlight=cls.__transform_highlights(hit),
                )
                for hit in results["hits"]["hits"]
            ],
            took=results["took"],
            total_hits=results["hits"]["total"]["value"],
            total_hits_relation=results["hits"]["total"]["relation"],
            max_score=results["hits"]["max_score"],
            index_creation_time=index_creation_time,
        )


SortingPreset = TypeAliasType(
    "SortingPreset", Literal["relevance", "text_level_position", "text_level_relevance"]
)


class GeneralSearchSettings(ModelBase):
    page: Annotated[int, conint(ge=1)] = 1
    page_size: Annotated[int, Literal[10, 25, 50]] = 10
    sorting_preset: Annotated[
        SortingPreset | None, Field(description="Sorting preset")
    ] = None
    strict: bool = False


class QuickSearchSettings(ModelBase):
    default_operator: Literal["AND", "OR"] = "OR"
    texts: (
        Annotated[
            list[PydanticObjectId],
            Field(
                description="IDs of texts to search in",
            ),
        ]
        | None
    ) = None

    @field_validator("default_operator", mode="before")
    @classmethod
    def default_operator_upper(cls, v: Any) -> str:
        return str(v).upper()


class AdvancedSearchSettings(ModelBase):
    pass


class QuickSearchRequestBody(ModelBase):
    search_type: Literal["quick"]
    query: Annotated[
        str,
        StringConstraints(max_length=512, strip_whitespace=True),
    ] = "*"
    settings_general: GeneralSearchSettings = GeneralSearchSettings()
    settings_quick: QuickSearchSettings = QuickSearchSettings()


class AdvancedSearchQuery(ModelBase):
    resource_queries: Annotated[
        list[AnyResourceSearchQuery],
        Field(discriminator="resource_type", max_length=64),
    ] = []


class AdvancedSearchRequestBody(ModelBase):
    search_type: Literal["advanced"]
    query: AdvancedSearchQuery = AdvancedSearchQuery()
    settings_general: GeneralSearchSettings = GeneralSearchSettings()
    settings_advanced: AdvancedSearchSettings = AdvancedSearchSettings()


SearchRequestBody = Annotated[
    Union[  # noqa: UP007
        QuickSearchRequestBody,
        AdvancedSearchRequestBody,
    ],
    Body(discriminator="search_type"),
]


class IndexInfoResponse(ModelBase):
    documents: int
    size: str
    searches: int
    last_indexed: datetime
