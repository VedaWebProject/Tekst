from tekst.models.settings import PlatformSettings, PlatformSettingsDocument


async def get_settings() -> PlatformSettingsDocument:
    return (
        await PlatformSettingsDocument.find_one()
        or await PlatformSettingsDocument.model_from(PlatformSettings()).create()
    )
