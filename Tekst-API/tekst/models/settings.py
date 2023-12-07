from typing import Annotated

from beanie import PydanticObjectId
from pydantic import EmailStr, Field, StringConstraints
from typing_extensions import TypedDict

from tekst.config import TekstConfig, get_config
from tekst.models.common import (
    CustomHttpUrl,
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


class PlatformDescriptionTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)
    ]


class PlatformNavInfoEntryTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=16)
    ]


class LayerCategoryTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)
    ]


class LayerCategory(TypedDict):
    key: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=16)
    ]
    translations: Translations[LayerCategoryTranslation]


class PlatformSettings(ModelBase, ModelFactoryMixin):
    """Settings defining platform behavior configured by admins"""

    # INFO

    info_platform_name: Annotated[
        str,
        StringConstraints(min_length=1, max_length=32),
        Field(description="Name of the platform"),
    ] = _cfg.info_platform_name
    info_subtitle: Annotated[
        Translations[PlatformDescriptionTranslation],
        Field(description="Short description of the platform, in multiple languages"),
    ] = [{"locale": "*", "translation": _cfg.info_subtitle}]
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

    # OPTIONS
    default_text_id: Annotated[
        PydanticObjectId | None, Field(description="Default text to load in UI")
    ] = None
    nav_info_entry: Annotated[
        Translations[PlatformNavInfoEntryTranslation],
        Field(description="Custom label for main navigation info entry"),
    ] = []
    layer_categories: Annotated[
        list[LayerCategory],
        Field(description="Layer categories to categorize layers in"),
    ] = []
    show_layer_category_headings: Annotated[
        bool, Field(description="Show layer category headings in browse view")
    ] = True
    always_show_text_info: Annotated[
        bool,
        Field(
            description=(
                "Always show text info and selector in header, "
                "even on non-text-specific pages"
            )
        ),
    ] = True
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
