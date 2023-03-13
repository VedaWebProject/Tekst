from fastapi import APIRouter, Depends

from textrig.config import TextRigConfig
from textrig.dependencies import get_cfg
from textrig.models.platform import PlatformData
from textrig.models.settings import PlatformSettingsDocument
from textrig.routers.texts import get_all_texts


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    responses={404: {"description": "Not found"}},
)


async def _get_platform_settings():
    return await PlatformSettingsDocument.find_all().first_or_none()


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=PlatformData,
    summary="Get platform data",
)
async def get_platform_data(cfg: TextRigConfig = Depends(get_cfg)) -> dict:
    """Returns data the client needs to initialize"""
    return PlatformData(
        texts=await get_all_texts(),
        settings=await _get_platform_settings(),
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
