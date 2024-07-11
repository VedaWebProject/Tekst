from tekst.models.settings import PlatformSettings, PlatformSettingsDocument


async def get_settings() -> PlatformSettingsDocument:
    return (
        await PlatformSettingsDocument.find_one()
        or await PlatformSettingsDocument.model_from(PlatformSettings()).create()
    )


async def update_settings(**kwargs) -> PlatformSettingsDocument:
    settings = await get_settings()
    for k, v in kwargs.items():
        setattr(settings, k, v)
    return await settings.replace()
