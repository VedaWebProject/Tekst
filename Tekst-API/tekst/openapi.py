from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig


tags_metadata = [
    {
        "name": "texts",
        "description": "Text-related operations",
        "externalDocs": {
            "description": "View external documentation",
            "url": "https://github.com/VedaWebProject/Tekst-API",
        },
    },
]


def process_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    # nothing happening here, yet
    return schema


def custom_openapi(app: FastAPI, cfg: TekstConfig):
    def _custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=cfg.info_platform_name,
            version=cfg.tekst_version,
            description=cfg.info_description,
            routes=app.routes,
            servers=[{"url": urljoin(str(cfg.server_url), str(cfg.api_path))}],
            terms_of_service=str(cfg.info_terms),
            tags=tags_metadata,
            contact={
                "name": cfg.info_contact_name,
                "url": cfg.info_contact_url,
                "email": cfg.info_contact_email,
            },
            license_info={
                "name": cfg.tekst_license,
                "url": cfg.tekst_license_url,
            },
        )
        app.openapi_schema = process_openapi_schema(openapi_schema)
        return app.openapi_schema

    app.openapi = _custom_openapi


async def generate_openapi_schema(
    to_file: bool, output_file: str, indent: int, sort_keys: bool, cfg: TekstConfig
) -> str:
    """
    Atomic operation for creating and processing the OpenAPI schema from outside of
    the app context. This is used in __main__.py
    """

    import json

    from asgi_lifespan import LifespanManager
    from httpx import AsyncClient

    from tekst.app import app

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get(f"{cfg.doc_openapi_url}")
            if resp.status_code != 200:
                raise HTTPException(resp.status_code)
            else:
                schema = resp.json()
                json_dump_args = {
                    "skipkeys": True,
                    "indent": indent or None,
                    "sort_keys": sort_keys,
                }
                if to_file:
                    with open(output_file, "w") as f:
                        json.dump(schema, f, **json_dump_args)
                return json.dumps(schema, **json_dump_args)
