from datetime import datetime
from typing import Any, Literal

from pydantic import field_validator

from tekst.models.common import ModelBase, PydanticObjectId


class SearchHit(ModelBase):
    id: PydanticObjectId
    label: str
    full_label: str
    text_id: PydanticObjectId
    level: int
    position: int
    score: float


class SearchResults(ModelBase):
    hits: list[SearchHit]
    took: int
    total_hits: int
    total_hits_relation: Literal["eq", "gte"]
    max_score: float | None
    index_creation_time: datetime

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
                )
                for hit in results["hits"]["hits"]
            ],
            took=results["took"],
            total_hits=results["hits"]["total"]["value"],
            total_hits_relation=results["hits"]["total"]["relation"],
            max_score=results["hits"]["max_score"],
            index_creation_time=index_creation_time,
        )


class SearchSettings(ModelBase):
    strict: bool = True
    default_operator: Literal["AND", "OR"] = "OR"

    @field_validator("default_operator", mode="before")
    @classmethod
    def default_operator_upper(cls, v: Any) -> Literal["AND", "OR"]:
        return str(v).upper()
