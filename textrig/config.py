from functools import lru_cache
from urllib.parse import quote as q

from pydantic import BaseSettings


class Config(BaseSettings):

    app_name: str = "TextRig"
    db_host: str = "127.0.0.1"
    db_port: int = 27017
    db_user: str = "root"
    db_pass: str = "root"

    def get_db_uri(self):
        return (
            f"mongodb://{self.db_user}:"
            f"{q(self.db_pass.encode('utf8'), safe='')}@"
            f"{q(self.db_host.encode('utf8'), safe='')}:{str(self.db_port)}"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_config():
    return Config()
