from functools import lru_cache
from urllib.parse import quote as q

from pydantic import BaseSettings, validator


class Config(BaseSettings):

    app_name: str = "TextRig"
    db_host: str = "127.0.0.1"
    db_port: str = "27017"
    db_user: str = "root"
    db_pass: str = "root"
    db_uri: str = f"mongodb://{db_user}:{q(db_pass.encode('utf8'))}@{db_host}:{db_port}"

    @validator("db_uri", pre=True)
    def val_db_uri(cls, _, values):
        return (
            f"mongodb://{values['db_user']}:"
            f"{q(values['db_pass'].encode('utf8'))}@"
            f"{values['db_host']}:{values['db_port']}"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_config():
    return Config()
