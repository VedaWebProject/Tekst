from typing import Annotated

from beanie import PydanticObjectId
from pydantic import EmailStr, Field, StringConstraints

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
    info_platform_name: Annotated[
        str, StringConstraints(min_length=1, max_length=32)
    ] = _cfg.info_platform_name
    info_description: Annotated[
        str | None, StringConstraints(max_length=128)
    ] = _cfg.info_description
    info_terms: Annotated[
        CustomHttpUrl | None, StringConstraints(max_length=512)
    ] = None
    info_contact_name: Annotated[
        str | None, StringConstraints(min_length=1, max_length=64)
    ] = None
    info_contact_url: Annotated[
        CustomHttpUrl | None, StringConstraints(max_length=512)
    ] = None
    info_contact_email: Annotated[
        EmailStr | None, StringConstraints(min_length=1, max_length=64)
    ] = None


class PlatformSettingsDocument(PlatformSettings, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "settings"


PlatformSettingsRead = PlatformSettings.get_read_model()
PlatformSettingsUpdate = PlatformSettings.get_update_model()
