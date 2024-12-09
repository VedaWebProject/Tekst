import json
import re

from pathlib import Path as PathObj
from typing import Annotated, Any, Union
from uuid import uuid4

from fastapi import APIRouter, Body, Request, status

from tekst import errors, search, tasks
from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.config import ConfigDep, TekstConfig
from tekst.models.resource import ResourceBaseDocument
from tekst.models.search import (
    AdvancedSearchRequestBody,
    IndexInfo,
    QuickSearchRequestBody,
    SearchResults,
)
from tekst.models.text import TextDocument
from tekst.state import get_state
from tekst.utils import client_hash, pick_translation


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
            queries=body.queries,
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
    # setup pagination for chunked search requests
    req_body.settings_general.pagination.page = 1
    req_body.settings_general.pagination.page_size = 50

    # prepare data needed for export data transformation
    locale = user.locale if user else None
    texts_by_ids = {str(txt.id): txt for txt in await TextDocument.find_all().to_list()}
    resources_by_ids = {
        str(res.id): res
        for res in await ResourceBaseDocument.find_all(with_children=True).to_list()
    }

    # perform search, transform data into target export data format
    hits = []
    while (results := await perform_search(user, req_body)).hits:
        # transform hits into actual search results export data
        for hit in results.hits:
            text = texts_by_ids.get(str(hit.text_id))
            hits.append(
                {
                    "location": hit.full_label,
                    "text": text.title,
                    "level": hit.level,
                    "levelLabel": pick_translation(text.levels[hit.level], locale),
                    "position": hit.position,
                    "score": hit.score,
                    "highlights": {
                        pick_translation(
                            resources_by_ids.get(hl_res_id).title, locale
                        ): hl
                        for hl_res_id, hl in hit.highlight.items()
                        if hl
                    },
                }
            )

        # break early if we already got all hits to avoid running into 10000 hits limit
        # that's enforced by the search routine
        if len(hits) >= results.total_hits:
            break
        # there's more, so advance pagination for the next search iteration
        req_body.settings_general.pagination.page += 1  # pragma: no cover

    # construct temp file name and path
    search_id = str(uuid4())
    tempfile_name = search_id
    tempfile_path: PathObj = cfg.temp_files_dir / tempfile_name

    # write temp file
    with tempfile_path.open("w") as f:
        json.dump(hits, f)

    # prepare download file info
    fmt = {
        "extension": "json",
        "mimetype": "application/json",
    }
    settings = await get_state()
    pf_title_safe = re.sub(r"[^a-zA-Z0-9]", "_", settings.platform_name).lower()
    filename = f"{pf_title_safe}_search_{search_id}.{fmt['extension']}"

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
    request: Request,
    cfg: ConfigDep,
) -> tasks.TaskDocument:
    return await tasks.create_task(
        _export_search_results_task,
        tasks.TaskType.SEARCH_EXPORT,
        user_id=user.id if user else None,
        target_id=user.id
        if user
        else client_hash(request, behind_reverse_proxy=cfg.behind_reverse_proxy),
        task_kwargs={
            "user": user,
            "cfg": cfg,
            "req_body": body,
        },
    )
