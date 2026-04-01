from typing import Annotated, Literal, TypeVar, get_args

from annotated_types import MaxLen
from typing_extensions import TypedDict


# LOCALE AND TRANSLATION TYPES

# type alias for available locale/language setting identifiers
type LocaleKey = Literal["deDE", "enUS"]
type TranslationLocaleKey = Literal["deDE", "enUS", "*"]


class TranslationBase(TypedDict):
    locale: TranslationLocaleKey


T = TypeVar("T", bound=TranslationBase)
Translations = Annotated[
    list[T],
    MaxLen(len(get_args(TranslationLocaleKey.__value__))),
]


def pick_translation(
    translations: list[TranslationBase],
    locale_key: LocaleKey = "enUS",
) -> str:
    prio = [locale_key, "*", "enUS"]
    sorted_translations = sorted(
        translations,
        key=lambda x: prio.index(x.get("locale")) if x.get("locale") in prio else 999,
    )
    return (
        sorted_translations[0].get("translation", "")
        if len(sorted_translations) > 0
        else ""
    )
