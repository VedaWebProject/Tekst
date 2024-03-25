import os

from functools import cache
from secrets import token_hex
from typing import Annotated
from urllib.parse import quote

from fastapi import Depends
from pydantic import (
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from tekst import package_metadata
from tekst.models.common import CustomHttpUrl
from tekst.utils import validators as val
from tekst.utils.strings import safe_name


_DEV_MODE: bool = bool(os.environ.get("TEKST_DEV_MODE", False))


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
    2. ".env.dev" if it exists AND if TEKST_DEV_MODE env var is set to true
    3. ".env.prod" if it exists
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
    if os.path.exists(f_env):
        env_files.append(f_env)
    if _DEV_MODE and os.path.exists(f_env_dev):
        env_files.append(f_env_dev)
    if os.path.exists(f_env_prod):  # pragma: no cover
        env_files.append(f_env_prod)
    if f_env_custom and os.path.exists(f_env_custom):  # pragma: no cover
        env_files.append(f_env_custom)
    return env_files


class TekstConfig(BaseSettings):
    """Platform config model"""

    model_config = SettingsConfigDict(
        env_file=_select_env_files(),
        env_file_encoding="utf-8",
        env_prefix="TEKST_",
        case_sensitive=False,
        secrets_dir="/run/secrets" if not _DEV_MODE else None,
        protected_namespaces=("model_",),
    )

    # basics
    server_url: CustomHttpUrl = "http://127.0.0.1:8000"
    web_path: str = "/"
    api_path: str = "/api"

    log_level: str = "warning"

    settings_cache_ttl: int = 60

    # development
    dev_mode: bool = False
    dev_host: str = "127.0.0.1"
    dev_port: int = 8000
    dev_use_xsrf_protection: bool = False
    dev_use_db: bool = True  # used internally for app init in different environments
    dev_use_es: bool = True  # used internally for app init in different environments

    # db-related config (MongoDB)
    db_protocol: str = "mongodb"
    db_host: str = "127.0.0.1"
    db_port: int = 27017
    db_user: str | None = None
    db_password: str | None = None
    db_name: str = "tekst"

    # Elasticsearch-related config
    es_protocol: str = "http"
    es_host: str = "127.0.0.1"
    es_port: int = 9200
    es_prefix: str = "tekst"
    es_init_timeout_s: int = 120

    # CORS
    cors_allow_origins: str | list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: str | list[str] = ["*"]
    cors_allow_headers: str | list[str] = ["*"]

    # Email-related config
    email_smtp_server: str | None = "127.0.0.1"
    email_smtp_port: int | None = 25
    email_smtp_user: str | None = None
    email_smtp_password: str | None = None
    email_smtp_starttls: bool = True
    email_from_address: str = "noreply@example-tekst-instance.org"

    # user messages config
    msg_force_delete_after_days: int = 365

    # security-related config
    security_secret: str = Field(default_factory=lambda: token_hex(32), min_length=16)
    security_closed_mode: bool = False
    security_users_active_by_default: bool = False

    security_enable_cookie_auth: bool = True
    security_auth_cookie_name: str = "tekstuserauth"
    security_auth_cookie_domain: str | None = None
    security_auth_cookie_lifetime: Annotated[int, Field(ge=3600)] = 43200
    security_access_token_lifetime: Annotated[int, Field(ge=3600)] = 43200

    security_enable_jwt_auth: bool = True
    security_auth_jwt_lifetime: Annotated[int, Field(ge=3600)] = 43200

    security_reset_pw_token_lifetime: Annotated[int, Field(ge=600)] = 3600  # 1h
    security_verification_token_lifetime: Annotated[int, Field(ge=600)] = 86400  # 24h

    security_init_admin_email: str | None = None
    security_init_admin_password: str | None = None

    # limits
    limits_max_resources_per_user: int = 10

    # documentation-related config (OpenAPI, Redoc)
    doc_openapi_url: str = "/openapi.json"
    doc_swaggerui_url: str = "/docs"
    doc_redoc_url: str = "/redoc"

    # general platform information config
    # (these are used as defaults in the platform settings)
    info_platform_name: Annotated[
        str, StringConstraints(min_length=1, max_length=32)
    ] = "Tekst"
    info_subtitle: Annotated[
        str | None,
        StringConstraints(max_length=128),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = "An online text research platform"
    info_terms: Annotated[
        CustomHttpUrl | None,
        StringConstraints(max_length=512),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = None
    info_contact_name: Annotated[
        str | None,
        StringConstraints(max_length=64),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = "Tekst Administrator"
    info_contact_email: Annotated[
        EmailStr | None,
        StringConstraints(max_length=64),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = "noreply@tekst-contact-email-not-set.com"
    info_contact_url: Annotated[
        CustomHttpUrl | None,
        StringConstraints(max_length=512),
        val.CleanupOneline,
        val.EmptyStringToNone,
    ] = None

    @field_validator("db_name", mode="after")
    @classmethod
    def generate_db_name(cls, v: str) -> str:
        return safe_name(v)

    @computed_field
    @property
    def tekst_info(self) -> dict[str, str]:
        info_data = {"name": "Tekst"}
        info_data.update(package_metadata)
        return info_data

    @computed_field
    @property
    def db_uri(self) -> str:
        db_password = quote(str(self.db_password).encode("utf8"), safe="")
        creds = f"{self.db_user}:{db_password}@" if self.db_user and db_password else ""
        return "{protocol}://{creds}{host}:{port}".format(
            protocol=self.db_protocol,
            creds=creds,
            host=quote(str(self.db_host).encode("utf8"), safe=""),
            port=str(self.db_port),
        )

    @computed_field
    @property
    def es_uri(self) -> str:
        return "{protocol}://{host}:{port}".format(
            protocol=self.es_protocol,
            host=quote(str(self.db_host).encode("utf8"), safe=""),
            port=str(self.es_port),
        )

    @field_validator(
        "cors_allow_origins", "cors_allow_methods", "cors_allow_headers", mode="after"
    )
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [e.strip() for e in v.split(",")]
        return v

    @field_validator("log_level", mode="after")
    @classmethod
    def uppercase_log_lvl(cls, v: str) -> str:
        return v.upper()

    def model_dump(
        self,
        *,
        include_keys_prefix: str = None,
        strip_include_keys_prefix: bool = False,
        **kwargs,
    ):
        if include_keys_prefix is None:
            return super().model_dump(**kwargs)
        if "include" in kwargs:
            raise AttributeError(
                "kwargs 'include_keys_prefix' and 'include' are exclusive"
            )
        includes_keys = {
            f for f in self.model_fields if f.startswith(include_keys_prefix)
        }
        return {
            k.removeprefix(include_keys_prefix if strip_include_keys_prefix else ""): v
            for k, v in super().model_dump(include=includes_keys, **kwargs).items()
        }


@cache
def get_config() -> TekstConfig:
    return TekstConfig()


ConfigDep = Annotated[TekstConfig, Depends(get_config)]
