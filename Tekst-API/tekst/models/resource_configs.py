from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase


class ResourceConfigBase(ModelBase):
    category: Annotated[
        str | None,
        StringConstraints(min_length=1, max_length=16, strip_whitespace=True),
        Field(description="Resource category key"),
    ] = None
    sort_order: Annotated[
        int,
        Field(description="Sort order for displaying this resource among others", ge=0),
    ] = 100
    default_active: Annotated[
        bool,
        Field(description="Whether this resource is active by default when public"),
    ] = True
    show_on_parent_level: Annotated[
        bool,
        Field(
            description="Show combined contents of this resource on the parent level"
        ),
    ] = False


class DeepLLinksConfig(ModelBase):
    _DEEPL_LANGUAGES: tuple = (
        "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI",
        "FR", "HU", "ID", "IT", "JA", "LT", "LV", "NL", "PL",
        "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH",
    )  # fmt: skip

    enabled: Annotated[
        bool, Field(description="Enable/disable quick translation links to DeepL")
    ] = False
    source_language: Annotated[
        Literal[_DEEPL_LANGUAGES] | None,
        Field(description="Source language"),
    ] = _DEEPL_LANGUAGES[0]
    languages: Annotated[
        list[Literal[_DEEPL_LANGUAGES]],
        Field(description="Target languages to display links for", max_length=32),
    ] = ["EN", "DE"]
