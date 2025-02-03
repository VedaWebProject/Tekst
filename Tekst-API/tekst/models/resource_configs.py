from typing import Annotated

from pydantic import Field

from tekst.models.common import ModelBase
from tekst.models.platform import OskKey
from tekst.types import ConStrOrNone


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
    ] = True
    show_on_parent_level: Annotated[
        bool,
        Field(
            description="Show combined contents of this resource on the parent level",
        ),
    ] = False
    searchable_quick: Annotated[
        bool,
        Field(
            description="Whether this resource should be included in quick search",
        ),
    ] = True
    searchable_adv: Annotated[
        bool,
        Field(
            description="Whether this resource should accessible via advanced search",
        ),
    ] = True
    rtl: Annotated[
        bool,
        Field(
            description="Whether to display text contents in right-to-left direction",
        ),
    ] = False
    osk: OskKey | None = None


class ResourceConfigBase(ModelBase):
    common: CommonResourceConfig = CommonResourceConfig()
