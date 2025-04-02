from os import environ
from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig, get_config
from tekst.i18n import pick_translation
from tekst.models.platform import PlatformState
from tekst.openapi.tags_metadata import get_tags_metadata


def customize_openapi(app: FastAPI, state: PlatformState):
    def _custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = generate_schema(app, state)
        return app.openapi_schema

    app.openapi = _custom_openapi


def generate_schema(app: FastAPI, state: PlatformState):
    cfg: TekstConfig = get_config()
    api_url = urljoin(str(cfg.server_url), str(cfg.api_path))
    schema = get_openapi(
        title=state.platform_name,
        version=cfg.tekst["version"],
        summary=cfg.api_doc.summary or pick_translation(state.platform_subtitle),
        description=cfg.api_doc.description,
        routes=app.routes,
        servers=[{"url": api_url}],
        terms_of_service=cfg.api_doc.terms_url,
        tags=get_tags_metadata(documentation_url=cfg.tekst["documentation"]),
        contact={
            "name": cfg.api_doc.contact_name,
            "url": cfg.api_doc.contact_url,
            "email": cfg.api_doc.contact_email,
        },
        license_info={
            "name": cfg.api_doc.license_name,
            "identifier": cfg.api_doc.license_id,
            "url": cfg.api_doc.license_url,
        }
        if cfg.api_doc.license_name
        else None,
        separate_input_output_schemas=False,
    )
    return process_openapi_schema(schema=schema)


def process_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    return schema


async def generate_openapi_json(
    to_file: bool = True,
    output_file: str = "openapi.json",
    indent: int = 2,
    sort_keys: bool = False,
) -> str:  # pragma: no cover
    """
    Atomic operation for creating and processing the OpenAPI schema from outside of
    the app context. This is used in __main__.py
    """
    environ["TEKST_NO_SERVICES"] = "true"
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
