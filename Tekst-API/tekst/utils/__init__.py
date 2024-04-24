from collections.abc import Iterator
from tempfile import TemporaryDirectory

from tekst.models.common import LocaleKey, Translations


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


async def get_temp_dir() -> Iterator[str]:
    dir = TemporaryDirectory()
    try:
        yield dir.name
    except Exception:
        raise
    finally:
        del dir
