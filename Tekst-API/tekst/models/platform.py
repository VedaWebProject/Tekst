from beanie import PydanticObjectId
from humps import camelize

from tekst.config import TekstConfig, get_config
from tekst.models.common import ModelBase
from tekst.models.segment import ClientSegmentHead, ClientSegmentRead
from tekst.models.settings import PlatformSettingsRead
from tekst.models.text import TextRead


_cfg: TekstConfig = get_config()


class PlatformSecurityInfo(ModelBase):
    closed_mode: bool = _cfg.security.closed_mode
    users_active_by_default: bool = _cfg.security.users_active_by_default
    enable_cookie_auth: bool = _cfg.security.enable_cookie_auth
    enable_jwt_auth: bool = _cfg.security.enable_jwt_auth
    auth_cookie_lifetime: int = _cfg.security.auth_cookie_lifetime


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    texts: list[TextRead]
    settings: PlatformSettingsRead
    security: PlatformSecurityInfo = PlatformSecurityInfo()
    system_segments: list[ClientSegmentRead]
    info_segments: list[ClientSegmentHead]
    settings_cache_ttl: int = _cfg.settings_cache_ttl
    tekst: dict[str, str] = camelize(_cfg.info.tekst)


class TextStats(ModelBase):
    """Text statistics data"""

    id: PydanticObjectId
    locations_count: int
    resources_count: int
    resource_types: dict[str, int]


class PlatformStats(ModelBase):
    """Platform statistics data"""

    users_count: int
    texts: list[TextStats]
