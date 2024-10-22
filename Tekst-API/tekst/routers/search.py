import json
import re

from pathlib import Path as PathObj
from typing import Annotated, Any, Union
from uuid import uuid4

from fastapi import APIRouter, Body, status

from tekst import errors, search, tasks
from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.config import ConfigDep, TekstConfig
from tekst.models.search import (
    AdvancedSearchRequestBody,
    IndexInfo,
    QuickSearchRequestBody,
    SearchHit,
    SearchResults,
)
from tekst.state import get_state


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SearchResults,
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
    response_model=tasks.TaskRead,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_search_index(su: SuperuserDep) -> tasks.TaskDocument:
    return await search.create_indices(user=su, force=True)


@router.get(
    "/index/info",
    response_model=list[IndexInfo],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_search_index_info(su: SuperuserDep) -> list[IndexInfo]:
    return await search.get_indices_info()


async def _export_search_results_task(
    user: OptionalUserDep,
    cfg: TekstConfig,
    req_body: QuickSearchRequestBody | AdvancedSearchRequestBody,
) -> dict[str, Any]:
    # perform search, collect hits
    hits: list[SearchHit] = []
    while (results := await perform_search(user, req_body)).hits:
        hits.extend(results.hits)
        req_body.settings_general.pagination.page += 1

    # constrct actual search results export data
    # ...

    # construct temp file name and path
    search_uuid = str(uuid4())
    tempfile_name = search_uuid
    tempfile_path: PathObj = cfg.temp_files_dir / tempfile_name

    # write temp file
    with tempfile_path.open("w") as f:
        json.dump(
            [hit.model_dump(by_alias=True) for hit in hits],
            f,
        )

    # prepare download file info
    fmt = {
        "extension": "json",
        "mimetype": "application/json",
    }
    settings = await get_state()
    pf_title_safe = re.sub(r"[^a-zA-Z0-9]", "_", settings.platform_name).lower()
    filename = f"{pf_title_safe}_search_{search_uuid}.{fmt['extension']}"

    # schedule generated temp file for delayed deletion
    tasks.delete_temp_file_after(tempfile_name)

    return {
        "filename": filename,
        "artifact": tempfile_name,
        "mimetype": fmt["mimetype"],
    }


@router.post(
    "/export",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=tasks.TaskRead,
)
async def export_search_results(
    user: OptionalUserDep,
    body: Annotated[
        Union[  # noqa: UP007
            QuickSearchRequestBody,
            AdvancedSearchRequestBody,
        ],
        Body(discriminator="search_type"),
    ],
    cfg: ConfigDep,
) -> tasks.TaskDocument:
    return await tasks.create_task(
        _export_search_results_task,
        tasks.TaskType.SEARCH_EXPORT,
        user_id=user.id if user else None,
        task_kwargs={
            "user": user,
            "cfg": cfg,
            "req_body": body,
        },
    )
