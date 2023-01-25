import sys

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from textrig.config import TextRigConfig, get_config
from textrig.db import init_odm
from textrig.dependencies import get_db, get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.routers import setup_routes
from textrig.tags import tags_metadata


_cfg: TextRigConfig = get_config()  # get (possibly cached) config data
setup_logging()  # set up logging to match prod/dev requirements

# create FastAPI app instance
app = FastAPI(
    root_path=_cfg.root_path,
    title=_cfg.app_name,
    description=_cfg.info.description,
    version=_cfg.info.version,
    terms_of_service=_cfg.info.terms,
    contact={
        "name": _cfg.info.contact_name,
        "url": _cfg.info.contact_url,
        "email": _cfg.info.contact_email,
    },
    license_info={
        "name": _cfg.info.license,
        "url": _cfg.info.license_url,
    },
    openapi_tags=tags_metadata,
    openapi_url=_cfg.doc.openapi_url,
    docs_url=_cfg.doc.swaggerui_url,
    redoc_url=_cfg.doc.redoc_url,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
    },
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

    # configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cfg.cors_allow_origins,
        allow_credentials=_cfg.cors_allow_credentials,
        allow_methods=_cfg.cors_allow_methods,
        allow_headers=_cfg.cors_allow_headers,
    )

    # init app peripherals
    init_layer_type_manager()
    setup_routes(app)

    # this is ugly, but unfortunately we don't have access to FastAPI's
    # dependency injection system in these lifecycle routines, so we have to
    # pass all these things by hand...
    await init_odm(get_db(get_db_client(_cfg), _cfg))

    # add root route to redirect to docs
    @app.get("/", response_class=RedirectResponse, status_code=301)
    async def root_redirect():
        return _cfg.doc.redoc_url

    # log dev server info for quick browser access
    if _cfg.dev_mode:  # pragma: no cover
        dev_base_url = f"http://{_cfg.uvicorn_host}:{_cfg.uvicorn_port}"
        if _cfg.doc.swaggerui_url:
            log.info(f"\u2022 SwaggerUI docs: {dev_base_url}{_cfg.doc.swaggerui_url}")
        if _cfg.doc.redoc_url:
            log.info(f"\u2022 Redoc API docs: {dev_base_url}{_cfg.doc.redoc_url}")


@app.on_event("shutdown")
async def shutdown_routine() -> None:
    log.info(f"{_cfg.info.platform} cleaning up and shutting down")
    get_db_client(_cfg).close()  # again, no DI possible here :(
