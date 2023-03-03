import os

from functools import lru_cache
from secrets import token_hex
from urllib.parse import quote

from pydantic import BaseSettings, EmailStr, Field, HttpUrl, validator

from textrig import pkg_meta
from textrig.models.common import ModelBase
from textrig.utils.strings import safe_name


def _select_env_files() -> list[str]:
    """
    Selects the dotenv (.env) files to load.
    Values from these files override the default
    values used in the config model classes.

    Selection and priority work as follows:

    - A maximum of two env files will be loaded (".env" and a second one)
    - Additional env files override values found in ".env"
    - If one additional env file is found, selection is complete

    Selection steps:

    1. ".env" if it exists
    2. Custom env file defined in "TEXTRIG_ENV_FILE" env var if it exists
    3. ".env.dev" if it exists AND if TEXTRIG_DEV_MODE env var is set to true
    4. ".env.prod" if it exists

    :return: List of .env file paths
    :rtype: list[str]
    """
    env_files = []
    # define used env file names
    f_env = ".env"
    f_env_dev = ".env.dev"
    f_env_prod = ".env.prod"
    f_env_custom = os.environ.get("TEXTRIG_ENV_FILE")
    # prio logic
    if os.path.exists(f_env):
        env_files.append(f_env)
    if f_env_custom and os.path.exists(f_env_custom):
        env_files.append(f_env_custom)
    elif os.environ.get("TEXTRIG_DEV_MODE") and os.path.exists(f_env_dev):
        env_files.append(f_env_dev)
    elif os.path.exists(f_env_prod):
        env_files.append(f_env_prod)
    return env_files


class DbConfig(ModelBase):
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


class DocConfig(ModelBase):
    """Documentation config model"""

    openapi_url: str = "/openapi.json"
    swaggerui_url: str = "/docs"
    redoc_url: str = "/redoc"


class InfoConfig(ModelBase):
    """General information config model"""

    platform_name: str = "TextRig"
    description: str = "An online text research platform"
    terms: HttpUrl = "https://www.example-textrig-instance.org/terms"
    contact_name: str = "Rick Sanchez"
    contact_url: HttpUrl = "https://www.example-textrig-instance.org/contact"
    contact_email: EmailStr = "rick.sanchez@example-textrig-instance.org"


class TextRigInfoConfig(ModelBase):
    """
    TextRig platform information config model

    These values are not configurable. They are taken from the package infos and
    aren't meant to be changed by users creating an own instance of the platform.
    """

    name: str = Field("TextRig", const=True)
    version: str = Field(pkg_meta["version"], const=True)
    description: str = Field(pkg_meta["description"], const=True)
    website: HttpUrl = Field(pkg_meta["website"], const=True)
    license: str = Field(pkg_meta["license"], const=True)
    license_url: HttpUrl = Field(pkg_meta["license_url"], const=True)


class SecurityConfig(ModelBase):
    """Security config model"""

    secret: str = Field(default_factory=lambda: token_hex(32), min_length=16)
    users_active_by_default: bool = False
    users_need_verification: bool = True
    auth_cookie_name: str = "textriguserauth"
    auth_cookie_domain: str | None = None
    auth_cookie_lifetime: int = 3600
    access_token_lifetime: int = 3600
    reset_pw_token_lifetime: int = 3600
    verification_token_lifetime: int = 3600
    jwt_lifetime: int = 3600
    csrf_cookie_name: str = "XSRF-TOKEN"
    csrf_header_name: str = "X-XSRF-TOKEN"


class TextRigConfig(BaseSettings):
    """Platform config model"""

    # basic
    dev_mode: bool = False
    root_path: str = ""
    server_url: HttpUrl = "http://127.0.0.1:8000"
    user_files_dir: str = "userfiles"
    log_level: str = "INFO"

    # uvicorn asgi binding
    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = 8000

    # CORS
    cors_allow_origins: str | list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: str | list[str] = ["*"]
    cors_allow_headers: str | list[str] = ["*"]

    # special domain sub configs
    security: SecurityConfig = SecurityConfig()  # security-related config
    db: DbConfig = DbConfig()  # db-related config (MongoDB)
    doc: DocConfig = DocConfig()  # documentation-related config (OpenAPI, Redoc)
    info: InfoConfig = InfoConfig()  # general platform information config
    textrig_info: TextRigInfoConfig = TextRigInfoConfig()  # TextRig information config

    @validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        pre=True,
    )
    def split_cors(cls, v):
        if isinstance(v, list):
            return [str(e) for e in v]
        if isinstance(v, str):
            return [e.strip() for e in v.split(",")]
        raise TypeError("Value must be a string or list of strings")

    @validator("log_level")
    def uppercase_log_lvl(cls, v: str) -> str:
        return v.upper()

    class Config:
        env_file = _select_env_files()
        env_prefix = "TEXTRIG_"
        env_nested_delimiter = "__"
        case_sensitive = False


@lru_cache
def get_config() -> TextRigConfig:
    return TextRigConfig()
