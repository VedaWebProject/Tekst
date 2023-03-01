from typing import Any

from fastapi import APIRouter, Depends
from humps import camelize

from textrig.config import TextRigConfig
from textrig.dependencies import get_cfg
from textrig.routers.texts import get_all_texts


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    responses={404: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=dict[str, Any],
    summary="Get platform data",
)
async def get_platform_data(cfg: TextRigConfig = Depends(get_cfg)) -> dict:
    """Returns data the client needs to initialize"""
    return camelize(
        {
            "info": cfg.info.dict(),
            "textrigInfo": cfg.textrig_info.dict(),
            "texts": await get_all_texts(),
            "security": {
                "usersActiveByDefault": cfg.security.users_active_by_default,
                "usersNeedVerification": cfg.security.users_need_verification,
            },
        }
    )


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
