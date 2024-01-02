from time import monotonic

from tekst.config import TekstConfig, get_config
from tekst.models.settings import PlatformSettingsDocument


_cfg: TekstConfig = get_config()
_settings = None
_last_refresh = -1


async def get_settings(nocache: bool = False) -> PlatformSettingsDocument:
    global _settings, _last_refresh
    if (
        not nocache
        and _settings
        and (monotonic() - _last_refresh) < _cfg.settings_cache_ttl
    ):
        # cache hit
        return _settings  # pragma: no cover
    _settings = (
        await PlatformSettingsDocument.find_one()
        or await PlatformSettingsDocument().create()
    )
    _last_refresh = monotonic()
    return _settings
