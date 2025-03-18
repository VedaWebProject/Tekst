from typing import Annotated

from pydantic import Field
from typing_extensions import TypeAliasType, TypedDict

from tekst.i18n import TranslationBase, Translations
from tekst.models.common import ModelBase
from tekst.models.platform import OskKey
from tekst.types import ConStr, ConStrOrNone, SchemaOptionalNonNullable


class CommonResourceConfig(ModelBase):
    category: Annotated[
        ConStrOrNone(
            max_length=16,
        ),
        Field(
            description="Resource category key",
        ),
    ] = None
    sort_order: Annotated[
        int,
        Field(
            description="Sort order for displaying this resource among others",
            ge=0,
            le=1000,
        ),
    ] = 10
    default_active: Annotated[
        bool,
        Field(
            description="Whether this resource is active by default when public",
        ),
        SchemaOptionalNonNullable,
    ] = True
    enable_content_context: Annotated[
        bool,
        Field(
            description="Show combined contents of this resource on the parent level",
        ),
        SchemaOptionalNonNullable,
    ] = False
    searchable_quick: Annotated[
        bool,
        Field(
            description="Whether this resource should be included in quick search",
        ),
        SchemaOptionalNonNullable,
    ] = True
    searchable_adv: Annotated[
        bool,
        Field(
            description="Whether this resource should accessible via advanced search",
        ),
        SchemaOptionalNonNullable,
    ] = True
    rtl: Annotated[
        bool,
        Field(
            description="Whether to display text contents in right-to-left direction",
        ),
        SchemaOptionalNonNullable,
    ] = False
    osk: OskKey | None = None


class ResourceConfigBase(ModelBase):
    common: CommonResourceConfig = CommonResourceConfig()


# GENERIC RESOURCE CONFIG: ITEM DISPLAY (ORDER, GROUPING AND TRANSLATIONS)


class ItemsDisplayTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=128,
            cleanup="oneline",
        ),
        Field(
            description="Translation of an item or item group name",
        ),
    ]


_ItemName = ConStr(
    max_length=32,
    cleanup="oneline",
)
ItemName = TypeAliasType(
    "ItemName",
    Annotated[
        _ItemName,
        Field(description="Name of an item"),
    ],
)
ItemGroupName = TypeAliasType(
    "ItemGroupName",
    Annotated[
        _ItemName,
        Field(description="Name of an item group"),
    ],
)


class ItemGroup(TypedDict):
    name: ItemGroupName
    translations: Annotated[
        Translations[ItemsDisplayTranslation],
        Field(description="Translations for the name of the item group"),
    ]


class ItemDisplayProps(TypedDict):
    name: ItemName
    translations: Annotated[
        Translations[ItemsDisplayTranslation],
        Field(description="Translations for the name of the item"),
    ]
    group: ItemGroupName
