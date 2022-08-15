import os
from functools import lru_cache
from urllib.parse import quote as q

from pydantic import BaseModel, BaseSettings, Field
from textrig import pkg_meta


class DbConfig(BaseModel):
    """Database config model"""

    protocol: str = "mongodb"
    host: str = "localhost"
    port: int = 27017
    user: str = "root"
    password: str = "root"

    def get_db_uri(self):
        return (
            f"{self.protocol}://{self.user}:"
            f"{q(self.password.encode('utf8'), safe='')}@"
            f"{q(self.host.encode('utf8'), safe='')}:{str(self.port)}"
        )


class DocConfig(BaseModel):
    """Documentation config model"""

    openapi_url: str = "/openapi.json"
    swaggerui_url: str = "/docs"
    redoc_url: str = "/redoc"


class InfoConfig(BaseModel):
    """General information config model"""

    platform: str = Field("TextRig", const=True)
    platform_website: str = Field(pkg_meta["website"], const=True)
    license: str = Field(pkg_meta["license"], const=True)
    license_url: str = Field(pkg_meta["license_url"], const=True)
    version: str = Field(pkg_meta["version"], const=True)
    description: str = pkg_meta["description"]
    long_description: str = pkg_meta["long_description"]
    website: str = pkg_meta["website"]
    terms: str = pkg_meta["website"]
    contact_name: str = ""
    contact_url: str = ""
    contact_email: str = ""


class TextRigConfig(BaseSettings):
    """Platform config model"""

    # basic
    app_name: str = "TextRig"
    dev_mode: bool = False
    test_mode: bool = False
    root_path: str = ""

    # special domain
    db: DbConfig = DbConfig()  # db cfg (MongoDB)
    doc: DocConfig = DocConfig()  # doc cfg (SwaggerUI, Redoc, OpenAPI)
    info: InfoConfig = InfoConfig()  # general information cfg

    class Config:
        env_nested_delimiter = "__"
        case_sensitive = False


@lru_cache()
def get_config():
    return TextRigConfig(
        _env_file=".env.dev" if os.environ.get("DEV_MODE") else ".env.prod"
    )
