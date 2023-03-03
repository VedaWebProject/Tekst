from pydantic import Field

from textrig.config import InfoConfig, TextRigConfig, TextRigInfoConfig, get_config
from textrig.models.common import ModelBase
from textrig.models.text import TextRead


_cfg: TextRigConfig = get_config()  # get (possibly cached) config data


class PlatformSecurityInfo(ModelBase):
    users_active_by_default: bool = _cfg.security.users_active_by_default
    users_need_verification: bool = _cfg.security.users_need_verification


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    info: InfoConfig = _cfg.info
    textrig_info: TextRigInfoConfig = _cfg.textrig_info
    texts: list[TextRead]
    security: PlatformSecurityInfo = Field(default_factory=PlatformSecurityInfo)
