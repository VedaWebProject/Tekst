from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig, get_config
from tekst.models.settings import PlatformSettings
from tekst.openapi.tags_metadata import get_tags_metadata
from tekst.utils import pick_translation


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


def customize_openapi(app: FastAPI, settings: PlatformSettings):
    def _custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = generate_schema(app, settings)
        return app.openapi_schema

    app.openapi = _custom_openapi


def generate_schema(app: FastAPI, settings: PlatformSettings):
    schema = get_openapi(
        title=settings.info_platform_name,
        version=_cfg.info.tekst["version"],
        description=pick_translation(settings.info_subtitle),
        routes=app.routes,
        servers=[{"url": urljoin(str(_cfg.server_url), str(_cfg.api_path))}],
        terms_of_service=_cfg.info.terms_url,
        tags=get_tags_metadata(documentation_url=_cfg.info.tekst["documentation"]),
        contact={
            "name": _cfg.info.contact_name,
            "url": _cfg.info.contact_url,
            "email": _cfg.info.contact_email,
        },
        license_info={
            "name": _cfg.info.tekst["license"],
            "url": _cfg.info.tekst["license_url"],
        },
        separate_input_output_schemas=False,
    )
    return process_openapi_schema(schema=schema)


def process_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    return schema


async def generate_openapi_schema(
    to_file: bool = True,
    output_file: str = "openapi.json",
    indent: int = 2,
    sort_keys: bool = False,
) -> str:  # pragma: no cover
    """
    Atomic operation for creating and processing the OpenAPI schema from outside of
    the app context. This is used in __main__.py
    """

    import json

    from asgi_lifespan import LifespanManager

    from tekst.app import app

    async with LifespanManager(app):  # noqa: SIM117
        schema = app.openapi()
        json_dump_kwargs = {
            "skipkeys": True,
            "indent": indent or None,
            "sort_keys": sort_keys,
        }
        if to_file:
            with open(output_file, "w") as f:
                json.dump(schema, f, **json_dump_kwargs)
        return json.dumps(schema, **json_dump_kwargs)
