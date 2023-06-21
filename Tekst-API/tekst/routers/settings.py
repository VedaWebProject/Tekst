from fastapi import APIRouter, status

from tekst.auth import SuperuserDep
from tekst.models.settings import (
    PlatformSettingsDocument,
    PlatformSettingsRead,
    PlatformSettingsUpdate,
)


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.patch("", response_model=PlatformSettingsRead, status_code=status.HTTP_200_OK)
async def update_platform_settings(
    su: SuperuserDep,
    settings_updates: PlatformSettingsUpdate,
) -> PlatformSettingsRead:
    settings_doc = await PlatformSettingsDocument.find_all().first_or_none()
    if not settings_doc:
        # create from defaults
        settings_doc = await PlatformSettingsDocument().create()
    await settings_doc.apply(settings_updates.dict(exclude_unset=True))
    return settings_doc
