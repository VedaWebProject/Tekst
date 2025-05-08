from typing import Literal, TypeVar, get_args

from pydantic import conlist
from typing_extensions import TypedDict


# LOCALE AND TRANSLATION TYPES

# type alias for available locale/language setting identifiers
_platform_locales = ("deDE", "enUS")
type LocaleKey = Literal[_platform_locales]
type TranslationLocaleKey = Literal[_platform_locales + ("*",)]


class TranslationBase(TypedDict):
    locale: TranslationLocaleKey


T = TypeVar("T", bound=TranslationBase)
Translations = conlist(
    T,
    max_length=len(get_args(TranslationLocaleKey.__value__)),
)


def pick_translation(translations: Translations, locale_key: LocaleKey = "enUS") -> str:
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
