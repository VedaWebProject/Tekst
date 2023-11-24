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

    info_platform_name: Annotated[
        str,
        StringConstraints(min_length=1, max_length=32),
        Field(description="Name of the platform"),
    ] = _cfg.info_platform_name
    info_description: Annotated[
        str | None,
        StringConstraints(max_length=128),
        Field(description="Short description of the platform"),
    ] = _cfg.info_description
    info_terms: Annotated[
        CustomHttpUrl | None,
        StringConstraints(max_length=512),
        Field(description="URL to page with terms and conditions for API usage"),
    ] = None
    info_contact_name: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=64),
        Field(description="Platform contact name"),
    ] = None
    info_contact_email: Annotated[
        EmailStr | None,
        StringConstraints(min_length=1, max_length=64),
        Field(description="Platform contact email"),
    ] = None
    info_contact_url: Annotated[
        CustomHttpUrl | None,
        StringConstraints(max_length=512),
        Field(description="URL to page with contact info"),
    ] = None

    default_text_id: Annotated[
        PydanticObjectId | None, Field(description="Default text to load in UI")
    ] = None
    show_header_info: Annotated[
        bool, Field(description="Show platform description in header")
    ] = True
    show_footer_info: Annotated[
        bool, Field(description="Show platform title and description in footer")
    ] = True


class PlatformSettingsDocument(PlatformSettings, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "settings"


PlatformSettingsRead = PlatformSettings.read_model()
PlatformSettingsUpdate = PlatformSettings.update_model()
