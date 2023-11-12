from typing import Annotated

from beanie import PydanticObjectId
from pydantic import EmailStr, Field

from tekst.config import TekstConfig, get_config
from tekst.models.common import (
    CustomHttpUrl,
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


class PlatformSettings(ModelBase, ModelFactoryMixin):
    """Settings defining platform behavior configured by admins"""

    default_text_id: Annotated[
        PydanticObjectId | None, Field(description="Default text to load in UI")
    ] = None

    # general platform information config
    info_platform_name: str = _cfg.info_platform_name
    info_description: str = _cfg.info_description
    info_terms: CustomHttpUrl = _cfg.info_terms
    info_contact_name: str = _cfg.info_contact_name
    info_contact_url: CustomHttpUrl = _cfg.info_contact_url
    info_contact_email: EmailStr = _cfg.info_contact_email


class PlatformSettingsDocument(PlatformSettings, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "settings"


PlatformSettingsRead = PlatformSettings.get_read_model()
PlatformSettingsUpdate = PlatformSettings.get_update_model()
