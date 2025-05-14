import gc
import re

from contextlib import asynccontextmanager
from os import getenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette_csrf import CSRFMiddleware

from tekst import db, search
from tekst.config import TekstConfig, get_config
from tekst.db import migrations
from tekst.errors import TekstHTTPException
from tekst.logs import log
from tekst.middlewares import CookieTypeChoiceMiddleware
from tekst.models.platform import PlatformState
from tekst.openapi import customize_openapi
from tekst.routers import setup_routes
from tekst.state import get_state


_NO_SERVICES = getenv("TEKST_NO_SERVICES", False)
_cfg: TekstConfig = get_config()  # get (possibly cached) config data


async def startup_routine(app: FastAPI) -> None:
    setup_routes(app)

    if not _NO_SERVICES:
        # init DB connection and ODM
        await db.init_odm()
        # get platform state from DB
        state = await get_state()
        # check for pending migrations, exit (non-0) if any are found
        if not _cfg.dev_mode:  # pragma: no cover
            await migrations.check_for_migrations(
                db_version=state.db_version,
                auto_migrate=False,
            )
        # init ES client
        await search.init_es_client()
    else:  # pragma: no cover
        state = PlatformState()

    customize_openapi(app=app, state=state)

    if not _cfg.email.smtp_server:
        log.warning("No SMTP server configured")  # pragma: no cover

    # Hello World!
    log.info(
        f"{state.platform_name} ({_cfg.tekst['name']} "
        f"Server v{_cfg.tekst['version']}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )


async def shutdown_routine(app: FastAPI) -> None:
    log.info(f"{_cfg.tekst['name']} cleaning up and shutting down...")
    if not _NO_SERVICES:
        await db.close()
        await search.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_routine(app)
    yield
    await shutdown_routine(app)


# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.api_path,
    openapi_url=_cfg.api_doc.openapi_url,
    docs_url=_cfg.api_doc.swaggerui_url,
    redoc_url=_cfg.api_doc.redoc_url,
    lifespan=lifespan,
    separate_input_output_schemas=False,
)

# add middleware to force use of session cookies if a request to the cookie-based
# login endpoint does NOT carry a truthy value for the `persistent` form field
app.add_middleware(CookieTypeChoiceMiddleware)

# add and configure XSRF/CSRF middleware
if not _cfg.dev_mode or _cfg.xsrf:  # pragma: no cover
    app.add_middleware(
        CSRFMiddleware,
        secret=_cfg.security.secret,
        required_urls=[re.compile(r".*/auth/cookie/login.*")],
        exempt_urls=[re.compile(r".*/auth/cookie/logout.*")],
        sensitive_cookies={_cfg.security.auth_cookie_name},
        cookie_name="XSRF-TOKEN",
        cookie_path="/",
        cookie_domain=_cfg.security.auth_cookie_domain or None,
        cookie_secure=not _cfg.dev_mode,
        cookie_samesite="Lax",
        header_name="X-XSRF-TOKEN",
    )

# add and configure CORS middleware
if _cfg.cors.enable:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cfg.cors.allow_origins,
        allow_credentials=_cfg.cors.allow_credentials,
        allow_methods=_cfg.cors.allow_methods,
        allow_headers=_cfg.cors.allow_headers,
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: Exception):
    # force garbage collection due to issues with custom exception handler
    # (see https://github.com/fastapi/fastapi/discussions/9145#discussioncomment-7254388)
    gc.collect()
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=exc.status_code,
            detail=exc.detail.model_dump().get("detail", None),
            headers=exc.headers,
        )
        if isinstance(exc, TekstHTTPException)
        else exc,
    )
