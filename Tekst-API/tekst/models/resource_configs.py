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
    group: ItemGroupName | None = None

    @classmethod
    def sort_items_keys(
        cls,
        item_keys: list[ItemName],
        *,
        item_groups: list[ItemGroup] = [],
        item_display_props: list["ItemDisplayProps"] = [],
    ) -> list[ItemName]:
        # get order of metadata groups from config
        groups_order = [g.get("name") for g in item_groups]
        # get general order of metadata keys from config
        keys_order = [dp.get("name") for dp in item_display_props]
        # sort keys based on groups order, then general keys order
        keys_order = sorted(
            keys_order,
            key=lambda k: (
                groups_order.index(k) if k in groups_order else len(groups_order),
                keys_order.index(k),
            ),
        )
        # create final sorted list of metadata keys, including keys
        # that are not present in the item_display_props
        return sorted(
            item_keys,
            key=lambda k: (
                keys_order.index(k) if k in keys_order else len(keys_order),
                k,  # alphabetical secondary sorting
            ),
        )
