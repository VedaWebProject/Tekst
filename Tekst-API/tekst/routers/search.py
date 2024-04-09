from typing import Annotated, Union

from fastapi import APIRouter, BackgroundTasks, Body, status

from tekst import errors, locks, search
from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.models.search import (
    AdvancedSearchRequestBody,
    IndexInfoResponse,
    QuickSearchRequestBody,
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
    body: Annotated[
        Union[  # noqa: UP007
            QuickSearchRequestBody,
            AdvancedSearchRequestBody,
        ],
        Body(discriminator="search_type"),
    ],
) -> SearchResults:
    if (
        body.settings_general.pagination.es_from()
        + body.settings_general.pagination.es_size()
    ) > 10000:
        raise errors.E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS
    if body.search_type == "quick":
        return await search.search_quick(
            user=user,
            query_string=body.query,
            settings_general=body.settings_general,
            settings_quick=body.settings_quick,
        )
    elif body.search_type == "advanced":
        return await search.search_advanced(
            user=user,
            queries=body.query,
            settings_general=body.settings_general,
            settings_advanced=body.settings_advanced,
        )


@router.get(
    "/index/create",
    status_code=status.HTTP_202_ACCEPTED,
    responses=errors.responses(
        [
            errors.E_409_ACTION_LOCKED,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_search_index(
    su: SuperuserDep, background_tasks: BackgroundTasks
) -> None:
    if await locks.is_locked(locks.LockKey.INDEX_CREATE_UPDATE):
        raise errors.E_409_ACTION_LOCKED
    background_tasks.add_task(search.create_index)


@router.get(
    "/index/info",
    response_model=IndexInfoResponse,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_search_index_info(su: SuperuserDep) -> IndexInfoResponse:
    return await search.get_index_info()
