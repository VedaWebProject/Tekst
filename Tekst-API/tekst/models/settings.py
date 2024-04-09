from typing import Annotated, get_args

from beanie import PydanticObjectId
from pydantic import EmailStr, Field, StringConstraints
from typing_extensions import TypedDict

from tekst.config import TekstConfig, get_config
from tekst.models.common import (
    CustomHttpUrl,
    LocaleKey,
    ModelBase,
    ModelFactoryMixin,
    PlatformStateDocumentBase,
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


class PlatformNavInfoEntryTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
        ),
    ]


class ResourceCategoryTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]


class ResourceCategory(TypedDict):
    key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
        ),
    ]
    translations: Translations[ResourceCategoryTranslation]


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

    info_platform_name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
        Field(
            description="Name of the platform",
        ),
    ] = _cfg.info_platform_name
    info_subtitle: Annotated[
        Translations[PlatformDescriptionTranslation],
        Field(
            description="Short description of the platform, in multiple languages",
        ),
    ] = [{"locale": "*", "translation": _cfg.info_subtitle}]
    info_terms: Annotated[
        CustomHttpUrl | None,
        StringConstraints(
            max_length=512,
        ),
        Field(
            description="URL to page with terms and conditions for API usage",
        ),
    ] = _cfg.info_terms
    info_contact_name: Annotated[
        str | None,
        StringConstraints(
            max_length=64,
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
        Field(
            description="Platform contact name",
        ),
    ] = _cfg.info_contact_name
    info_contact_email: Annotated[
        EmailStr | None,
        StringConstraints(
            max_length=64,
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
        Field(description="Platform contact email"),
    ] = _cfg.info_contact_email
    info_contact_url: Annotated[
        CustomHttpUrl | None,
        StringConstraints(
            max_length=512,
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
        Field(
            description="URL to page with contact info",
        ),
    ] = _cfg.info_contact_url

    # OPTIONS
    default_text_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="Default text to load in UI",
        ),
    ] = None
    nav_info_entry: Annotated[
        Translations[PlatformNavInfoEntryTranslation],
        Field(
            description="Custom label for main navigation info entry",
        ),
    ] = []
    resource_categories: Annotated[
        list[ResourceCategory],
        Field(
            description="Resource categories to categorize resources in",
            max_length=32,
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
    always_show_resource_category_headings: Annotated[
        bool,
        Field(
            description="Show category heading for the only category with resources",
        ),
    ] = False
    always_show_text_info: Annotated[
        bool,
        Field(
            description=(
                "Always show text info and selector in header, "
                "even on non-text-specific pages"
            ),
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


class PlatformSettingsDocument(PlatformSettings, PlatformStateDocumentBase):
    pass


PlatformSettingsRead = PlatformSettings.read_model()
PlatformSettingsUpdate = PlatformSettings.update_model()
