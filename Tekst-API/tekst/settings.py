from time import monotonic

from tekst.models.settings import PlatformSettingsDocument, PlatformSettingsRead


_settings = None
_cache_ttl = 60
_last_refresh = (_cache_ttl + 1) * -1


async def get_settings(force_nocache: bool = False) -> PlatformSettingsRead:
    global _settings, _last_refresh, _cache_ttl
    if not force_nocache and _settings and (monotonic() - _last_refresh) < _cache_ttl:
        # cache hit
        return _settings
    from_db = await PlatformSettingsDocument.find_one()
    if from_db is None:
        from_db = await PlatformSettingsDocument().create()
    _last_refresh = monotonic()
    _settings = PlatformSettingsRead.model_from(from_db)
    return _settings
