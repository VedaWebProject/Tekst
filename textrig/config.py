import os
from functools import lru_cache
from urllib.parse import quote

from pydantic import BaseModel, BaseSettings, EmailStr, Field, HttpUrl, validator
from textrig import pkg_meta
from textrig.utils.strings import safe_name


class DbConfig(BaseModel):
    """Database config model"""

    protocol: str = "mongodb"
    host: str = "localhost"
    port: int = 27017
    user: str = "root"
    password: str = "root"
    name: str = "textrig"

    @validator("host", "password", pre=True)
    def url_quote(cls, v) -> str:
        return quote(str(v).encode("utf8"), safe="")

    @validator("name", always=True)
    def generate_db_name(cls, v) -> str:
        return safe_name(v)

    def get_uri(self) -> str:
        creds = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"{self.protocol}://{creds}{self.host}:{str(self.port)}"


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
    website: HttpUrl = pkg_meta["website"]
    terms: HttpUrl = pkg_meta["website"]
    contact_name: str = ""
    contact_url: HttpUrl = ""
    contact_email: EmailStr = ""


class TextRigConfig(BaseSettings):
    """Platform config model"""

    # basic
    env_file: str = ".env.prod"
    app_name: str = "TextRig"
    dev_mode: bool = False
    root_path: str = ""
    snippets_dir: str = "/snippets"
    log_level: str = "INFO"

    # uvicorn asgi binding
    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = 8000

    # special domain sub configs
    db: DbConfig = DbConfig()  # db cfg (MongoDB)
    doc: DocConfig = DocConfig()  # doc cfg (SwaggerUI, Redoc, OpenAPI)
    info: InfoConfig = InfoConfig()  # general information cfg

    def __init__(self, env_file: str = ".env", *args, **kwargs):
        super().__init__(*args, env_file=env_file, _env_file=env_file, **kwargs)

    @validator("log_level")
    def uppercase_log_lvl(cls, v: str) -> str:
        return v.upper()

    class Config:
        env_prefix = "TR_"
        env_nested_delimiter = "__"
        case_sensitive = False


@lru_cache
def get_config() -> TextRigConfig:
    env_file = ".env.prod"
    if os.path.exists(".env"):
        env_file = ".env"
    if os.environ.get("TR_DEV_MODE") and os.path.exists(".env.dev"):
        env_file = ".env.dev"
    if os.environ.get("TR_ENV_FILE") and os.path.exists(os.environ.get("TR_ENV_FILE")):
        env_file = os.environ.get("TR_ENV_FILE")
    return TextRigConfig(env_file=env_file)
