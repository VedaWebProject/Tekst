from fastapi import APIRouter, status

from tekst import search
from tekst.models.search import (
    SearchRequestBody,
    SearchResults,
)


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post(
    "",
    response_model=SearchResults,
    status_code=status.HTTP_200_OK,
)
async def perform_search(
    body: SearchRequestBody,
) -> SearchResults:
    if body.search_type == "quick":
        return search.search_quick(
            query=body.query,
            settings=body.settings,
        )
    elif body.search_type == "advanced":
        return search.search_advanced(
            query=body.query,
            settings=body.settings,
        )
