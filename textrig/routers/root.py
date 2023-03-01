from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from textrig.config import TextRigConfig, get_config


router = APIRouter(
    responses={status.HTTP_301_MOVED_PERMANENTLY: {"description": "Moved permanently"}},
)


@router.get(
    "/", response_class=RedirectResponse, status_code=301, include_in_schema=False
)
async def root_redirect(cfg: TextRigConfig = Depends(get_config)):
    return cfg.root_path + cfg.doc.redoc_url
