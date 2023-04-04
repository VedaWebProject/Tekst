import re
import sys

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from textrig.auth import create_sample_users
from textrig.config import TextRigConfig, get_config
from textrig.db import init_odm, reset_db
from textrig.dependencies import get_db, get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.models.settings import PlatformSettingsDocument
from textrig.openapi import custom_openapi
from textrig.routers import setup_routes
from textrig.sample_data import create_sample_texts


_cfg: TextRigConfig = get_config()  # get (possibly cached) config data
setup_logging()  # set up logging to match prod/dev requirements


async def startup_routine(app: FastAPI) -> None:
    # dev mode preparations
    if _cfg.dev_mode:
        # blank line for visual separation of app runs in dev mode
        print(file=sys.stderr)

    # Hello World!
    log.info(
        f"{_cfg.info.platform_name} ({_cfg.textrig_info.name} "
        f"Server v{_cfg.textrig_info.version}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    # init app peripherals
    init_layer_type_manager()
    setup_routes(app)

    # reset db (only in dev mode!)
    if _cfg.dev_mode:
        log.debug("Resetting DB...")
        await reset_db()

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

    # create/insert dev mode sample data
    if _cfg.dev_mode:
        log.info("Running development mode initialization routine...")
        log.debug("Creating sample users...")
        await create_sample_users()
        log.debug("Creating sample texts...")
        await create_sample_texts()

    # create inital platform settings from defaults
    log.info("Creating initial platform settings from defaults...")
    await PlatformSettingsDocument().create()


async def shutdown_routine(app: FastAPI) -> None:
    log.info(f"{_cfg.textrig_info.name} cleaning up and shutting down")
    get_db_client(_cfg).close()  # again, no DI possible here :(


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_routine(app)
    yield
    await shutdown_routine(app)


# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.root_path,
    openapi_url=_cfg.doc.openapi_url,
    docs_url=_cfg.doc.swaggerui_url,
    redoc_url=_cfg.doc.redoc_url,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
    },
    lifespan=lifespan,
)

# add and configure CSRF middleware
if not _cfg.dev_mode:
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
