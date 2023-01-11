from typing import Any

from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig
from textrig.db.io import DbIO
from textrig.dependencies import get_cfg, get_db_io
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
async def uidata(
    cfg: TextRigConfig = Depends(get_cfg), db_io: DbIO = Depends(get_db_io)
) -> dict:
    """Returns data the client needs to initialize"""
    return {
        "platform": await uidata_platform(cfg),
        "texts": await get_all_texts(db_io),
    }


@router.get("/platform", response_model=dict[str, str], summary="Platform metadata")
async def uidata_platform(cfg: TextRigConfig = Depends(get_cfg)) -> dict:
    """Returns platform metadata, possibly customized for this platform instance."""
    return dict(title=cfg.app_name, **cfg.info.dict())


@router.get("/i18n", summary="Get server-managed translations")
async def uidata_i18n(lang: str = None) -> dict:
    """Returns server-managed translations."""
    translations = {
        "deDE": {"general": {"welcome": '"Willkommen!", sagt der Server!'}},
        "enUS": {"general": {"welcome": '"Welcome!", says the server!'}},
    }
    if lang and lang in translations:
        return translations[lang]
    else:
        return translations
