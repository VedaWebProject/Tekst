from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TextRig"
    admin_email: str = "lol@lol.de"
    items_per_user: int = 50


@lru_cache()
def get_settings():
    return Settings()
