from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig, get_config
from tekst.models.platform import PlatformState
from tekst.openapi.tags_metadata import get_tags_metadata
from tekst.utils import pick_translation


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


def customize_openapi(app: FastAPI, settings: PlatformState):
    def _custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = generate_schema(app, settings)
        return app.openapi_schema

    app.openapi = _custom_openapi


def generate_schema(app: FastAPI, settings: PlatformState):
    api_url = urljoin(str(_cfg.server_url), str(_cfg.api_path))
    schema = get_openapi(
        title=settings.platform_name,
        version=_cfg.tekst["version"],
        summary=_cfg.api_doc.summary or pick_translation(settings.platform_subtitle),
        description=_cfg.api_doc.description,
        routes=app.routes,
        servers=[{"url": api_url}],
        terms_of_service=_cfg.api_doc.terms_url,
        tags=get_tags_metadata(documentation_url=_cfg.tekst["documentation"]),
        contact={
            "name": _cfg.api_doc.contact_name,
            "url": _cfg.api_doc.contact_url,
            "email": _cfg.api_doc.contact_email,
        },
        license_info={
            "name": _cfg.api_doc.license_name,
            "identifier": _cfg.api_doc.license_id,
            "url": _cfg.api_doc.license_url,
        }
        if _cfg.api_doc.license_name
        else None,
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
