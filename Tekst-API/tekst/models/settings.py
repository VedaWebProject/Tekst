from datetime import datetime
from typing import Annotated, get_args

from beanie import PydanticObjectId
from pydantic import Field, StringConstraints

from tekst.config import TekstConfig, get_config
from tekst.models.common import (
    DocumentBase,
    LocaleKey,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)
from tekst.utils import validators as val


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


class PlatformDescriptionTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=128,
            strip_whitespace=True,
        ),
    ]


class MainNavEntryTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
        ),
    ]


class OskMode(ModelBase):
    key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    font: Annotated[
        str | None,
        StringConstraints(
            max_length=32,
            strip_whitespace=True,
        ),
        val.EmptyStringToNone,
    ] = None


class PlatformSettings(ModelBase, ModelFactoryMixin):
    """Settings defining platform behavior configured by admins"""

    # INFO

    platform_name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
        Field(
            description="Name of the platform",
        ),
    ] = _cfg.api_doc.title or "Tekst"
    platform_subtitle: Annotated[
        Translations[PlatformDescriptionTranslation],
        Field(
            description="Short description of the platform, in multiple languages",
        ),
    ] = [
        {
            "locale": "*",
            "translation": _cfg.api_doc.summary or "An online text research platform",
        }
    ]

    # OPTIONS
    default_text_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="Default text to load in UI",
        ),
    ] = None
    nav_browse_entry: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation browse entry",
        ),
    ] = []
    nav_search_entry: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation search entry",
        ),
    ] = []
    nav_info_entry: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation info entry",
        ),
    ] = []
    custom_fonts: Annotated[
        list[
            Annotated[
                str,
                StringConstraints(
                    min_length=1,
                    max_length=32,
                    strip_whitespace=True,
                ),
            ]
        ],
        Field(
            description="CSS font family names for use in resources",
            max_length=64,
        ),
    ] = []
    show_resource_category_headings: Annotated[
        bool,
        Field(
            description="Show resource category headings in browse view",
        ),
    ] = True
    prioritize_browse_level_resources: Annotated[
        bool,
        Field(
            description=(
                "Display resources of current browse level before others in browse view"
            ),
        ),
    ] = True
    always_show_text_info: Annotated[
        bool,
        Field(
            description=(
                "Always show text info and selector in header, "
                "even on non-text-specific pages"
            ),
        ),
    ] = True
    show_logo_on_loading_screen: Annotated[
        bool,
        Field(
            description="Show logo on loading screen",
        ),
    ] = True
    show_logo_in_header: Annotated[
        bool,
        Field(
            description="Show logo in page header",
        ),
    ] = True
    show_tekst_footer_hint: Annotated[
        bool,
        Field(
            description="Show a small hint to the Tekst software in the footer",
        ),
    ] = True
    available_locales: Annotated[
        list[LocaleKey],
        Field(
            descriptions="Locales available for use in platform client",
            max_length=len(get_args(LocaleKey.__value__)),
            min_length=1,
        ),
    ] = list(get_args(LocaleKey.__value__))
    osk_modes: Annotated[
        list[OskMode],
        Field(
            description="OSK modes available for use in platform client",
        ),
    ] = []
    indices_created_at: datetime | None = None


class PlatformSettingsDocument(PlatformSettings, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "settings"


PlatformSettingsRead = PlatformSettings.read_model()
PlatformSettingsUpdate = PlatformSettings.update_model()
