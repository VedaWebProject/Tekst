from fastapi import APIRouter, status

from tekst import errors, search
from tekst.auth import OptionalUserDep
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
    responses=errors.responses(
        [
            errors.E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS,
        ]
    ),
)
async def perform_search(
    user: OptionalUserDep,
    body: SearchRequestBody,
) -> SearchResults:
    if (
        (body.settings_general.page - 1) * body.settings_general.page_size
    ) + body.settings_general.page_size > 10000:
        raise errors.E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS
    if body.search_type == "quick":
        return await search.search_quick(
            user=user,
            query=body.query,
            settings_general=body.settings_general,
            settings_quick=body.settings_quick,
        )
    elif body.search_type == "advanced":
        return await search.search_advanced(
            user=user,
            query=body.query,
            settings_general=body.settings_general,
            settings_advanced=body.settings_advanced,
        )
