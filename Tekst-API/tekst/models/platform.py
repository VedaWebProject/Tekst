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
from tekst.models.segment import ClientSegmentHead, ClientSegmentRead
from tekst.models.text import TextRead
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
            max_length=42,
            strip_whitespace=True,
        ),
    ]


class RegisterIntroTextTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=500,
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


class PlatformState(ModelBase, ModelFactoryMixin):
    """Platform state model holding platform settings and state data"""

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

    available_locales: Annotated[
        list[LocaleKey],
        Field(
            description="Locales available for use in platform client",
            max_length=len(get_args(LocaleKey.__value__)),
            min_length=1,
        ),
    ] = list(get_args(LocaleKey.__value__))

    default_text_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="Default text to load in UI",
        ),
    ] = None

    index_unpublished_resources: Annotated[
        bool,
        Field(
            description="Index unpublished resources",
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

    direct_jump_on_unique_alias_search: Annotated[
        bool,
        Field(
            description=(
                "Directly jump to respective location "
                "when searching for unique location alias"
            ),
        ),
    ] = True

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

    show_location_aliases: Annotated[
        bool,
        Field(
            description="Show location aliases in browse view",
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

    register_intro_text: Annotated[
        Translations[RegisterIntroTextTranslation],
        Field(
            description="Intro text shown in registration form",
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

    osk_modes: Annotated[
        list[OskMode],
        Field(
            description="OSK modes available for use in platform client",
        ),
    ] = []

    indices_updated_at: Annotated[
        datetime | None,
        Field(
            description="Time when indices were created",
        ),
    ] = None


class PlatformStateDocument(PlatformState, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "state"


PlatformStateRead = PlatformState.read_model()
PlatformStateUpdate = PlatformState.update_model()


class PlatformSecurityInfo(ModelBase):
    closed_mode: bool = _cfg.security.closed_mode
    users_active_by_default: bool = _cfg.security.users_active_by_default
    enable_cookie_auth: bool = _cfg.security.enable_cookie_auth
    enable_jwt_auth: bool = _cfg.security.enable_jwt_auth
    auth_cookie_lifetime: int = _cfg.security.auth_cookie_lifetime


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    texts: list[TextRead]
    state: PlatformStateRead
    security: PlatformSecurityInfo
    system_segments: list[ClientSegmentRead]
    info_segments: list[ClientSegmentHead]
    tekst: dict[str, str]
    max_field_mappings: int


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
