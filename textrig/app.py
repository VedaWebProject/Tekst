import re
import sys

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware
from textrig.auth import create_sample_users
from textrig.config import TextRigConfig, get_config
from textrig.db import init_odm
from textrig.dependencies import get_db, get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.openapi import custom_openapi
from textrig.routers import setup_routes


_cfg: TextRigConfig = get_config()  # get (possibly cached) config data
setup_logging()  # set up logging to match prod/dev requirements

# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.root_path,
    openapi_url=_cfg.doc.openapi_url,
    docs_url=_cfg.doc.swaggerui_url,
    redoc_url=_cfg.doc.redoc_url,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
    },
)

# add and configure CSRF middleware
app.add_middleware(
    CSRFMiddleware,
    secret=_cfg.security.secret,
    required_urls=[re.compile(r".*/auth/cookie/login.*")],
    exempt_urls=[re.compile(r".*/auth/cookie/logout.*")],
    sensitive_cookies={_cfg.security.auth_cookie_name},
    cookie_name=_cfg.security.csrf_cookie_name,
    cookie_path="/",
    cookie_domain=_cfg.security.auth_cookie_domain or None,
    cookie_secure=not _cfg.dev_mode,
    cookie_samesite="Lax",
    header_name=_cfg.security.csrf_header_name,
)

# add and configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cfg.cors_allow_origins,
    allow_credentials=_cfg.cors_allow_credentials,
    allow_methods=_cfg.cors_allow_methods,
    allow_headers=_cfg.cors_allow_headers,
)


@app.on_event("startup")
async def startup_routine() -> None:
    # dev mode preparations
    if _cfg.dev_mode:
        # blank line for visual separation of app runs in dev mode
        print(file=sys.stderr)

    # Hello World!
    log.info(
        f"{_cfg.app_name} (TextRig Server v{_cfg.info.version}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    # init app peripherals
    init_layer_type_manager()
    setup_routes(app)

    # this is ugly, but unfortunately we don't have access to FastAPI's
    # dependency injection system in these lifecycle routines, so we have to
    # pass all these things by hand...
    await init_odm(get_db(get_db_client(_cfg), _cfg))

    # log dev server info for quick browser access
    if _cfg.dev_mode:  # pragma: no cover
        api_path = _cfg.server_url + _cfg.root_path
        if _cfg.doc.swaggerui_url:
            log.info(f"\u2022 SwaggerUI docs @ {api_path}{_cfg.doc.swaggerui_url}")
        if _cfg.doc.redoc_url:
            log.info(f"\u2022 Redoc API docs @ {api_path}{_cfg.doc.redoc_url}")

    # modify and cache OpenAPI schema
    custom_openapi(app, _cfg)

    # create sample users for development
    if _cfg.dev_mode:
        log.info("Creating sample users for development...")
        await create_sample_users()


@app.on_event("shutdown")
async def shutdown_routine() -> None:
    log.info(f"{_cfg.info.platform} cleaning up and shutting down")
    get_db_client(_cfg).close()  # again, no DI possible here :(
