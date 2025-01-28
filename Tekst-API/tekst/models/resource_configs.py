from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.platform import OskKey
from tekst.utils import validators as val


class CommonResourceConfig(ModelBase):
    category: Annotated[
        str | None,
        StringConstraints(
            max_length=16,
            strip_whitespace=True,
        ),
        val.FalsyToNone,
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
    quick_searchable: Annotated[
        bool,
        Field(
            description="Whether this resource should be included in quick search",
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


# TYPE ANNOTATIONS FOR FIELD THAT CAN BE PART OF
# THE GENERAL TYPE-SPECIFIC RESOURCE CONFIGURATION

DefaultCollapsedConfigType = Annotated[
    bool,
    Field(
        description=(
            "Whether contents of this resource should be collapsed by default"
        ),
    ),
]

FontConfigType = Annotated[
    str | None,
    Field(
        description="Name of the font to use for this resource.",
    ),
]
