from functools import lru_cache
from urllib.parse import quote as q

from pydantic import BaseSettings, Field
from textrig import pkg_meta


class Config(BaseSettings):

    app_name: str = "TextRig"
    root_path: str = ""
    version: str = pkg_meta["version"]
    description: str = pkg_meta["description"]
    long_description: str = pkg_meta["long_description"]
    website: str = pkg_meta["website"]
    terms: str = pkg_meta["website"]
    contact_name: str = "Contact"
    contact_url: str = pkg_meta["website"]
    contact_email: str = ""

    platform: str = Field("TextRig", const=True)
    platform_website: str = Field(pkg_meta["website"], const=True)
    license: str = Field(pkg_meta["license"], const=True)
    license_url: str = Field(pkg_meta["license_url"], const=True)

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
