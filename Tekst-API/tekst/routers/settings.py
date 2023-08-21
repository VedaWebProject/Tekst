from typing import Annotated

from fastapi import APIRouter, Body, status

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
    settings_updates: Annotated[PlatformSettingsUpdate, Body(alias="settingsUpdates")],
) -> PlatformSettingsRead:
    settings_doc = await PlatformSettingsDocument.find_all().first_or_none()
    if not settings_doc:
        # create from defaults
        settings_doc = await PlatformSettingsDocument().create()
    await settings_doc.apply(settings_updates.model_dump(exclude_unset=True))
    return settings_doc
