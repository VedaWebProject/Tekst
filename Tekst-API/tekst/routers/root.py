from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from tekst.config import TekstConfig
from tekst.dependencies import get_cfg


router = APIRouter(
    responses={status.HTTP_301_MOVED_PERMANENTLY: {"description": "Moved permanently"}},
)


@router.get(
    "/", response_class=RedirectResponse, status_code=301, include_in_schema=False
)
async def root_redirect(cfg: Annotated[TekstConfig, Depends(get_cfg)]):
    return cfg.api_path + (cfg.doc_redoc_url or cfg.doc_swaggerui_url or "/platform")
