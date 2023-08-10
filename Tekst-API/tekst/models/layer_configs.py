from typing import Annotated, Literal

from pydantic import AfterValidator, Field

from tekst.models.common import LayerConfigBase


def _uppercase_lang_code(v):
    if v is None:
        return v
    if not isinstance(v, str):
        raise TypeError("Language codes have to be passed as strings")
    return v.upper()


class DeepLLinksConfig(LayerConfigBase):
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
        AfterValidator(_uppercase_lang_code),
        Field(description="Source language"),
    ] = _DEEPL_LANGUAGES[0]
    languages: Annotated[
        list[
            Annotated[Literal[_DEEPL_LANGUAGES], AfterValidator(_uppercase_lang_code)]
        ],
        Field(description="Target languages to display links for"),
    ] = ["EN", "DE"]
