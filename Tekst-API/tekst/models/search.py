from typing import Any, Literal

from pydantic import field_validator

from tekst.models.common import ModelBase, PydanticObjectId


class SearchHit(ModelBase):
    id: PydanticObjectId
    label: str
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

    @classmethod
    def from_es_results(cls, res: dict[str, Any]) -> "SearchResults":
        return cls(
            hits=[
                SearchHit(
                    id=hit["_id"],
                    label=hit["_source"]["label"],
                    text_id=hit["_source"]["text_id"],
                    level=hit["_source"]["level"],
                    position=hit["_source"]["position"],
                    score=hit["_score"],
                )
                for hit in res["hits"]["hits"]
            ],
            took=res["took"],
            total_hits=res["hits"]["total"]["value"],
            total_hits_relation=res["hits"]["total"]["relation"],
            max_score=res["hits"]["max_score"],
        )


class SearchSettings(ModelBase):
    strict: bool = True
    default_operator: Literal["AND", "OR"] = "OR"

    @field_validator("default_operator", mode="before")
    @classmethod
    def default_operator_upper(cls, v: Any) -> Literal["AND", "OR"]:
        return str(v).upper()
