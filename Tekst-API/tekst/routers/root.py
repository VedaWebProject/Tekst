from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from tekst.config import ConfigDep


router = APIRouter(
    responses={
        status.HTTP_307_TEMPORARY_REDIRECT: {"description": "Temporary Redirect"}
    },
)


@router.get(
    "/",
    response_class=RedirectResponse,
    status_code=307,
    include_in_schema=False,
)
async def root_redirect(cfg: ConfigDep):
    return cfg.api_path + (cfg.doc_redoc_url or cfg.doc_swaggerui_url or "/platform")
