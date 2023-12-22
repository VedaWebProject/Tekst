from typing import Annotated, Literal

from pydantic import Field

from tekst.models.common import ModelBase


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
