from time import monotonic

from tekst.models.settings import PlatformSettingsDocument


_settings = None
_cache_ttl = 60
_last_refresh = (_cache_ttl + 1) * -1


async def get_settings(force_nocache: bool = False) -> PlatformSettingsDocument:
    global _settings, _last_refresh, _cache_ttl
    if not force_nocache and _settings and (monotonic() - _last_refresh) < _cache_ttl:
        # cache hit
        return _settings
    _settings = await PlatformSettingsDocument.find_one()
    if not _settings:
        _settings = await PlatformSettingsDocument().create()
    _last_refresh = monotonic()
    return _settings
