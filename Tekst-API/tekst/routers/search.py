from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from tekst import search
from tekst.models.search import SearchResults, SearchSettings


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get(
    "/quick",
    response_model=SearchResults,
    status_code=status.HTTP_200_OK,
)
async def quick_search(
    q: Annotated[str, Query(description="Query string")] = "*",
    strict: Annotated[bool, Query(description="Strict search")] = True,
    default_operator: Annotated[
        Literal["AND", "OR", "and", "or"],
        Query(description="Default operator", alias="op"),
    ] = "OR",
) -> SearchResults:
    return search.search_quick(
        query=q,
        settings=SearchSettings(
            strict=strict,
            default_operator=default_operator,
        ),
    )
