import re

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette_csrf import CSRFMiddleware

from tekst import db, search
from tekst.config import TekstConfig, get_config
from tekst.errors import TekstHTTPException
from tekst.logging import log, setup_logging
from tekst.models.settings import PlatformSettings
from tekst.openapi import customize_openapi
from tekst.resources import init_resource_types_mgr
from tekst.routers import setup_routes
from tekst.settings import get_settings


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
setup_logging()  # set up logging to match prod/dev requirements


async def startup_routine(app: FastAPI) -> None:
    init_resource_types_mgr()
    setup_routes(app)
    if not _cfg.dev_mode or _cfg.dev.use_db:
        await db.init_odm()
    if not _cfg.dev_mode or _cfg.dev.use_es:
        await search.init_es_client()

    settings = await get_settings() if _cfg.dev.use_db else PlatformSettings()
    customize_openapi(app=app, settings=settings)

    if not _cfg.email.smtp_server:
        log.warning("No SMTP server configured")  # pragma: no cover

    # Hello World!
    log.info(
        f"{settings.info_platform_name} ({_cfg.info.tekst['name']} "
        f"Server v{_cfg.info.tekst['version']}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )


async def shutdown_routine(app: FastAPI) -> None:
    log.info(f"{_cfg.info.tekst['name']} cleaning up and shutting down...")
    if not _cfg.dev_mode or _cfg.dev.use_db:
        db.close()
    if not _cfg.dev_mode or _cfg.dev.use_es:
        search.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_routine(app)
    yield
    await shutdown_routine(app)


# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.api_path,
    openapi_url=_cfg.doc.openapi_url,
    docs_url=_cfg.doc.swaggerui_url,
    redoc_url=_cfg.doc.redoc_url,
    lifespan=lifespan,
    separate_input_output_schemas=False,
)

# add and configure XSRF/CSRF middleware
if not _cfg.dev_mode or _cfg.dev.use_xsrf_protection:  # pragma: no cover
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cfg.cors.allow_origins,
    allow_credentials=_cfg.cors.allow_credentials,
    allow_methods=_cfg.cors.allow_methods,
    allow_headers=_cfg.cors.allow_headers,
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
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
