from collections.abc import Iterator
from tempfile import TemporaryDirectory

from tekst.models.common import Translations


def pick_translation(translations: Translations, locale_key: str = "enUS") -> str:
    sorted_translations = sorted(
        translations, key=lambda x: [locale_key, "*", "enUS"].index(x.get("locale"))
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
