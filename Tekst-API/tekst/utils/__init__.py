from tekst.models.common import Translations


def pick_translation(translations: Translations, locale_key: str = "enUS") -> str:
    for translation in translations:
        if translation.get("locale", None) == locale_key:
            return translation.get("translation", "")
    for translation in translations:
        if translation.get("locale", None) == "*":
            return translation.get("translation", "")
    if len(translations) > 0:
        return translations[0].get("translation", "")
    return ""
