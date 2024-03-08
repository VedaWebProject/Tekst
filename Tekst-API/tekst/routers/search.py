from typing import Annotated

from fastapi import APIRouter, status, Body

from tekst import search
from tekst.models.search import (
    SearchResults,
    AdvancedSearchRequestBody,
    QuickSearchRequestBody,
)


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post(
    "/quick",
    response_model=SearchResults,
    status_code=status.HTTP_200_OK,
)
async def quick_search(
    body: QuickSearchRequestBody = QuickSearchRequestBody(),
) -> SearchResults:
    return search.search_quick(
        query=body.query,
        settings=body.settings,
    )


@router.post(
    "/advanced",
    response_model=SearchResults,
    status_code=status.HTTP_200_OK,
)
async def advanced_search(
    body: AdvancedSearchRequestBody = AdvancedSearchRequestBody(),
) -> SearchResults:
    return search.search_advanced(
        query=body.query,
        settings=body.settings,
    )
