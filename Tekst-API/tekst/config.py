import os
import re

from functools import cache
from os.path import realpath
from pathlib import Path
from secrets import token_hex
from typing import Annotated, Any
from urllib.parse import quote
from uuid import uuid4

from fastapi import Depends
from humps import camelize
from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    EmailStr,
    Field,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from tekst import package_metadata
from tekst.types import ConStr, ConStrOrNone, HttpUrl, HttpUrlOrNone


_DEV_MODE: bool = bool(os.environ.get("TEKST_DEV_MODE", False))


class ConfigSubSection(BaseModel):
    """Base class for config sub sections"""

    model_config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True,
        from_attributes=True,
        validate_assignment=True,  # should only happen in tests anyway
    )


def _select_env_files() -> list[str]:
    """
    Selects the dotenv (.env) files to load.
    Values from these files override the default
    values used in the config model classes.

    Selection and priority work as follows:

    - A maximum of three env files will be loaded
      (".env", one of ".env.dev" and ".env.prod",
      and, if defined, an additional custom env file)
    - Env files loaded later override values of env files loaded earlier

    Selection steps:

    1. ".env" if it exists
    2. ".env.dev" if it exists AND if TEKST_DEV_MODE env var is set to `true`
    3. ".env.prod" if it exists AND if TEKST_DEV_MODE env var is set to `false`
    4. Custom env file defined in "TEKST_CUSTOM_ENV_FILE" env var if it exists

    :return: List of .env file paths
    :rtype: list[str]
    """
    env_files = []
    # define used env file names
    f_env = ".env"
    f_env_dev = ".env.dev"
    f_env_prod = ".env.prod"
    f_env_custom = os.environ.get("TEKST_CUSTOM_ENV_FILE")
    # prio logic
    if os.path.exists(f_env):  # pragma: no cover
        env_files.append(f_env)
    if _DEV_MODE and os.path.exists(f_env_dev):
        env_files.append(f_env_dev)
    elif os.path.exists(f_env_prod):  # pragma: no cover
        env_files.append(f_env_prod)
    if f_env_custom and os.path.exists(f_env_custom):  # pragma: no cover
        env_files.append(f_env_custom)
    return env_files


class MongoDBConfig(ConfigSubSection):
    """Database config sub section model"""

    protocol: str = "mongodb"
    host: str = "127.0.0.1"
    port: int = 27017
    user: ConStrOrNone(
        cleanup="oneline",
        max_length=64,
    ) = None
    password: ConStrOrNone(
        cleanup="oneline",
        max_length=64,
    ) = None
    name: str = "tekst"

    @field_validator("name", mode="before")
    @classmethod
    def validate_db_name(cls, v: Any) -> str:
        if not isinstance(v, str):
            v = str(v)
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(f"Invalid database name: {v} (only [a-zA-Z0-9_] allowed)")
        return v

    @field_validator("host", "password", mode="before")
    @classmethod
    def url_quote(cls, v) -> str:
        if v is None:
            return v
        return quote(str(v).encode("utf8"), safe="")

    @computed_field
    @property
    def uri(self) -> str:
        creds = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"{self.protocol}://{creds}{self.host}:{str(self.port)}"


class ElasticsearchConfig(ConfigSubSection):
    """Elasticsearch config sub section model"""

    protocol: str = "http"
    host: str = "127.0.0.1"
    port: int = 9200
    prefix: str = "tekst"
    timeout_init_s: int = 240
    timeout_general_s: int = 30
    timeout_search_s: str = "30s"

    @field_validator("host", mode="before")
    @classmethod
    def url_quote(cls, v) -> str:
        if v is None:
            return v
        return quote(str(v).encode("utf8"), safe="")

    @field_validator("timeout_search_s", mode="before")
    @classmethod
    def timeout_int_to_time_value(cls, v) -> str:
        if isinstance(v, int):
            return f"{v}s"
        v = re.sub(r"\D", "", v)  # keep only digits
        if not v:
            return "30s"
        return f"{v}s"

    @computed_field
    @property
    def uri(self) -> str:
        return f"{self.protocol}://{self.host}:{str(self.port)}"


class SecurityConfig(ConfigSubSection):
    """Security config sub section model"""

    secret: ConStr(
        min_length=16,
        max_length=512,
        cleanup="oneline",
    ) = token_hex(32)
    closed_mode: bool = False
    users_active_by_default: bool = False

    enable_cookie_auth: bool = True
    auth_cookie_name: str = "tekstuserauth"
    auth_cookie_domain: ConStrOrNone(
        cleanup="oneline",
        max_length=64,
    ) = None
    auth_cookie_lifetime: Annotated[
        int,
        Field(ge=3600),
    ] = 43200
    access_token_lifetime: Annotated[
        int,
        Field(ge=3600),
    ] = 43200

    enable_jwt_auth: bool = False
    auth_jwt_lifetime: Annotated[
        int,
        Field(ge=3600),
    ] = 86400

    reset_pw_token_lifetime: Annotated[
        int,
        Field(ge=600),
    ] = 3600  # 1h
    verification_token_lifetime: Annotated[
        int,
        Field(ge=600),
    ] = 86400  # 24h

    init_admin_email: ConStrOrNone(
        max_length=256,
        cleanup="oneline",
    ) = None
    init_admin_password: ConStrOrNone(
        max_length=256,
        cleanup="oneline",
    ) = None


class EMailConfig(ConfigSubSection):
    """Email-related things config sub section model"""

    smtp_server: ConStr(
        max_length=256,
        cleanup="oneline",
    ) = "127.0.0.1"
    smtp_port: int | None = 25
    smtp_user: ConStrOrNone(
        max_length=256,
        cleanup="oneline",
    ) = None
    smtp_password: ConStrOrNone(
        max_length=256,
        cleanup="oneline",
    ) = None
    smtp_starttls: bool = True
    from_address: str = "noreply@example-tekst-instance.org"


class ApiDocConfig(ConfigSubSection):
    """Documentation config sub section model"""

    openapi_url: str = "/openapi.json"
    swaggerui_url: str = "/docs"
    redoc_url: str = "/redoc"

    title: ConStr(
        max_length=32,
        cleanup="oneline",
    ) = "Tekst"
    summary: ConStrOrNone(
        max_length=256,
        cleanup="oneline",
    ) = None
    description: ConStrOrNone(
        max_length=4096,
        cleanup="multiline",
    ) = None
    terms_url: HttpUrlOrNone = None
    contact_name: ConStrOrNone(
        max_length=64,
        cleanup="oneline",
    ) = None
    contact_email: EmailStr | None = None
    contact_url: HttpUrlOrNone = None
    license_name: ConStrOrNone(
        max_length=32,
        cleanup="oneline",
    ) = None
    license_id: ConStrOrNone(
        max_length=32,
        cleanup="oneline",
    ) = None
    license_url: HttpUrlOrNone = None


class CORSConfig(ConfigSubSection):
    """CORS config sub section model"""

    enable: bool = False
    allow_origins: str | list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: str | list[str] = ["*"]
    allow_headers: str | list[str] = ["*"]

    @field_validator("allow_origins", "allow_methods", "allow_headers", mode="after")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [e.strip() for e in v.split(",")]
        return v


class MiscConfig(ConfigSubSection):
    """Misc config sub section model"""

    usrmsg_force_delete_after_days: int = 365
    max_resources_per_user: int = 10
    del_exports_after_minutes: int = 5

    @computed_field
    @property
    def demo_data_path(self) -> str:
        return Path(realpath(__file__)).parent.parent / "demo"


class TekstConfig(BaseSettings):
    """Platform config model"""

    model_config = SettingsConfigDict(
        env_file=_select_env_files(),
        env_file_encoding="utf-8",
        env_prefix="TEKST_",
        env_nested_delimiter="__",
        populate_by_name=True,
        case_sensitive=False,
        protected_namespaces=("model_",),
        validate_assignment=True,  # should only happen in tests anyway
    )

    server_url: HttpUrl = "http://127.0.0.1:8000"
    api_path: str = "/api"
    web_path: str = "/"
    behind_reverse_proxy: bool = False

    dev_mode: bool = False
    log_level: str = "warning"
    auto_migrate: bool = False
    xsrf: bool = True

    temp_files_dir: DirectoryPath = "/tmp/tekst_tmp"

    # config sub sections
    db: MongoDBConfig = MongoDBConfig()  # MongoDB-related config
    es: ElasticsearchConfig = ElasticsearchConfig()  # Elasticsearch-related config
    security: SecurityConfig = SecurityConfig()  # security-related config
    email: EMailConfig = EMailConfig()  # Email-related config
    api_doc: ApiDocConfig = ApiDocConfig()  # API documentation-related config
    cors: CORSConfig = CORSConfig()  # CORS-related config
    misc: MiscConfig = MiscConfig()  # misc config

    @computed_field
    @property
    def tekst(self) -> dict[str, str]:
        return dict(name="Tekst", **package_metadata)

    @field_validator("dev_mode", mode="before")
    @classmethod
    def parse_dev_mode(cls, v: Any) -> bool:
        return False if str(v).lower() == "false" else bool(v)

    @field_validator("log_level", mode="after")
    @classmethod
    def uppercase_log_lvl(cls, v: str) -> str:
        return v.upper()

    @field_validator("temp_files_dir", mode="before")
    @classmethod
    def temp_dir_to_existing_path_obj(cls, v: Any) -> Path:
        try:
            path = Path(str(v))
            path.mkdir(parents=True, exist_ok=True)
            test_file_path = path / (str(uuid4()) + ".tmp")
            test_file_path.unlink(missing_ok=True)
            test_file_path.write_text(data="test")
            test_file_path.unlink(missing_ok=True)
        except Exception as e:
            print(e)
            raise ValueError(
                f"Temporary directoy is not valid or writable: {path}"
            ) from e
        return path


@cache
def get_config(log_level: str | None = None) -> TekstConfig:
    return TekstConfig(**({"log_level": log_level} if log_level else {}))


ConfigDep = Annotated[TekstConfig, Depends(get_config)]
