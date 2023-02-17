from typing import Any

from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig
from textrig.dependencies import get_cfg
from textrig.routers.texts import get_all_texts


router = APIRouter(
    prefix="/uidata",
    tags=["uidata"],
    responses={404: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=dict[str, Any],
    summary="Data the client needs to display in the UI",
)
async def get_platform_data(cfg: TextRigConfig = Depends(get_cfg)) -> dict:
    """Returns data the client needs to initialize"""
    return {
        "platform": await get_platform_info(cfg),
        "texts": await get_all_texts(),
        "security": {"usersActiveByDefault": cfg.security.users_active_by_default},
    }


@router.get("/platform", response_model=dict[str, str], summary="Platform metadata")
async def get_platform_info(cfg: TextRigConfig = Depends(get_cfg)) -> dict:
    """Returns platform metadata, possibly customized for this platform instance."""
    return dict(title=cfg.app_name, **cfg.info.dict())


@router.get("/i18n", summary="Get server-managed translations")
async def get_translations(lang: str = None) -> dict:
    """Returns server-managed translations."""
    translations = {
        "deDE": {"general": {"welcomeTest": '"Willkommen!", sagt der Server!'}},
        "enUS": {"general": {"welcomeTest": '"Welcome!", says the server!'}},
    }
    if lang and lang in translations:
        return translations[lang]
    else:
        return translations
