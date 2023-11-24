from typing import Annotated, Any

from beanie import PydanticObjectId
from humps import camelize
from pydantic import Field

from tekst.config import TekstConfig, get_config
from tekst.models.common import ModelBase
from tekst.models.segment import ClientSegmentHead, ClientSegmentRead
from tekst.models.settings import PlatformSettingsRead
from tekst.models.text import TextRead


_cfg: TekstConfig = get_config()


class PlatformSecurityInfo(ModelBase):
    closed_mode: bool = _cfg.security_closed_mode
    users_active_by_default: bool = _cfg.security_users_active_by_default
    enable_cookie_auth: bool = _cfg.security_enable_cookie_auth
    enable_jwt_auth: bool = _cfg.security_enable_jwt_auth
    auth_cookie_lifetime: int = _cfg.security_auth_cookie_lifetime


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    tekst: dict[str, Any] = camelize(
        _cfg.model_dump(include_keys_prefix="tekst_", strip_include_keys_prefix=True)
    )
    texts: list[TextRead]
    settings: PlatformSettingsRead
    security: PlatformSecurityInfo = PlatformSecurityInfo()
    system_segments: Annotated[list[ClientSegmentRead], Field(alias="systemSegments")]
    info_segments: Annotated[list[ClientSegmentHead], Field(alias="infoSegments")]


class TextStats(ModelBase):
    """Text statistics data"""

    id: PydanticObjectId
    nodes_count: int
    layers_count: int
    layer_types: dict[str, int]


class PlatformStats(ModelBase):
    """Platform statistics data"""

    users_count: int
    texts: list[TextStats]
