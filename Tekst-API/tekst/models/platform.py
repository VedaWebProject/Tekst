from typing import Annotated, get_args

from beanie import PydanticObjectId
from pydantic import AwareDatetime, Field, field_validator
from pydantic_extra_types.color import Color

from tekst.config import TekstConfig, get_config
from tekst.i18n import LocaleKey, TranslationBase, Translations
from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.segment import ClientSegmentHead, ClientSegmentRead
from tekst.models.text import TextRead
from tekst.models.user import UserRead
from tekst.types import (
    ColorSerializer,
    ConStr,
    ConStrOrNone,
    FontFamilyValue,
    FontFamilyValueOrNone,
)


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


class PlatformSubtitleTranslation(TranslationBase):
    translation: ConStr(max_length=128)


class MainNavEntryTranslation(TranslationBase):
    translation: ConStr(max_length=42)


class NavTranslations(ModelBase):
    browse: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation browse entry",
        ),
    ] = []
    search: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation search entry",
        ),
    ] = []
    info: Annotated[
        Translations[MainNavEntryTranslation],
        Field(
            description="Custom label for main navigation info entry",
        ),
    ] = []


class ResourceMetadataKeyTranslation(TranslationBase):
    translation: ConStr(max_length=64)


class ResourceMetadataKey(ModelBase):
    key: str
    translations: Translations[ResourceMetadataKeyTranslation]


OskKey = Annotated[
    ConStr(
        max_length=32,
    ),
    Field(
        description="Key identifying an OSK mode",
    ),
]


class OskMode(ModelBase):
    key: OskKey
    name: ConStr(
        max_length=32,
    )
    font: FontFamilyValueOrNone = None


class PlatformState(ModelBase, ModelFactoryMixin):
    """Platform state model holding platform settings and state data"""

    platform_name: Annotated[
        ConStr(
            max_length=32,
        ),
        Field(
            description="Name of the platform",
        ),
    ] = _cfg.api_doc.title or "Tekst"

    platform_subtitle: Annotated[
        Translations[PlatformSubtitleTranslation],
        Field(
            description=(
                "Short descriptive subtitle of the platform, in multiple languages"
            ),
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

    fonts: Annotated[
        list[FontFamilyValue],
        Field(
            description="CSS font family names for custom fonts",
            max_length=64,
        ),
    ] = []

    ui_font: Annotated[
        FontFamilyValueOrNone,
        Field(
            description=(
                "Font family used for non-content UI "
                "(Tekst default UI font used if not set)"
            ),
        ),
    ] = None

    content_font: Annotated[
        FontFamilyValueOrNone,
        Field(
            description=(
                "Default font family used for content "
                "(Tekst default content font used if not set)"
            ),
        ),
    ] = None

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

    direct_jump_on_unique_alias_search: Annotated[
        bool,
        Field(
            description=(
                "Directly jump to respective location "
                "when searching for unique location alias"
            ),
        ),
    ] = True

    nav_translations: Annotated[
        NavTranslations,
        Field(
            description="Custom labels for main navigation entries",
        ),
    ] = NavTranslations()

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

    ui_color: Annotated[
        Color,
        ColorSerializer,
        Field(
            description="Primary color used in for client UI",
        ),
    ] = "#305D97"

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

    deny_resource_types: Annotated[
        list[str],
        Field(
            description="Resource types regular users are not allowed to create",
            max_length=64,
        ),
    ] = ["apiCall"]

    osk_modes: Annotated[
        list[OskMode],
        Field(
            description="OSK modes available for use in platform client",
        ),
    ] = []

    res_meta_translations: Annotated[
        list[ResourceMetadataKey],
        Field(
            description="Custom labels for main navigation entries",
            max_length=64,
        ),
    ] = []

    indices_updated_at: Annotated[
        AwareDatetime | None,
        Field(
            description="Time when indices were created",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = None

    db_version: Annotated[
        ConStrOrNone(
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Version string of DB data",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = None

    @field_validator("deny_resource_types", mode="after")
    @classmethod
    def validate_deny_resource_types(cls, v):
        from tekst.resources import resource_types_mgr

        resource_type_names = resource_types_mgr.list_names()
        for res_type in v:
            if res_type not in resource_type_names:
                raise ValueError(
                    f"Given resource type ({res_type}) is not a valid "
                    f"resource type name (one of {resource_type_names})."
                )
        return v


class PlatformStateDocument(PlatformState, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "state"
        bson_encoders = {Color: lambda c: c.as_hex()}


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


class ClientInitData(ModelBase):
    platform: Annotated[
        PlatformData,
        Field(description="Platform data"),
    ]
    user: Annotated[
        UserRead | None,
        Field(description="User data of current user (if there is an active session)"),
    ] = None
