from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    app_name: str = "TextRig"
    db_host: str = "127.0.0.1"
    db_port: str = "27017"
    db_uri: str = f"mongodb://{db_host}:{db_port}"
    db_user: str = "root"
    db_pass: str = "root"


@lru_cache()
def get_config():
    return Config()
