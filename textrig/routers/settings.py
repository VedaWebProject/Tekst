from fastapi import APIRouter, status

from textrig.config import TextRigConfig, get_config
from textrig.models.settings import (
    PlatformSettingsDocument,
    PlatformSettingsRead,
    PlatformSettingsUpdate,
)


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.patch("", response_model=PlatformSettingsRead, status_code=status.HTTP_200_OK)
async def update_platform_settings(
    settings_updates: PlatformSettingsUpdate,
) -> PlatformSettingsRead:
    settings_doc = await PlatformSettingsDocument.find_all().first_or_none()
    if not settings_doc:
        # create from defaults
        settings_doc = await PlatformSettingsDocument().create()
    await settings_doc.set(settings_updates.dict(exclude_unset=True))
    return settings_doc
