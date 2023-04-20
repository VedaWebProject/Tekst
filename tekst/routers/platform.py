from fastapi import APIRouter, Depends

from tekst.config import TekstConfig
from tekst.dependencies import get_cfg
from tekst.layer_types import get_layer_types_info
from tekst.models.platform import PlatformData
from tekst.models.settings import PlatformSettingsDocument
from tekst.routers.texts import get_all_texts


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    responses={404: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=PlatformData,
    summary="Get platform data",
)
async def get_platform_data(cfg: TekstConfig = Depends(get_cfg)) -> dict:
    """Returns data the client needs to initialize"""
    return PlatformData(
        texts=await get_all_texts(),
        settings=await PlatformSettingsDocument.find_one({}),
        layer_types=get_layer_types_info(),
    )


@router.get("/i18n", summary="Get server-managed translations")
async def get_translations(lang: str = None) -> dict:
    """Returns server-managed translations."""
    translations = {
        "deDE": {"welcomeTest": '"Willkommen!", sagt der Server!'},
        "enUS": {"welcomeTest": '"Welcome!", says the server!'},
    }
    if lang and lang in translations:
        return translations[lang]
    else:
        return translations
