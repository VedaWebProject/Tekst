import sys

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from textrig.config import TextRigConfig, get_config
from textrig.db import init_odm
from textrig.dependencies import get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.routers import setup_routes
from textrig.tags import tags_metadata


# set up logging to match prod/dev requirements
setup_logging()

# get (possibly cached) config data
_cfg: TextRigConfig = get_config()


# def pre_startup_routine() -> None:
#     if _cfg.dev_mode:
#         # blank line for visual separation of app runs in dev mode
#         print(file=sys.stderr)

#     # Hello World!
#     log.info(
#         f"{_cfg.app_name} (TextRig Server v{_cfg.info.version}) "
#         f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
#     )

#     init_layer_type_manager()
#     setup_routes(app)


# initialize FastAPI app
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
    # on_startup=[startup_routine],
    # on_shutdown=[shutdown_routine],
)

# TODO: Properly configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cfg.cors_allow_origins,
    allow_credentials=_cfg.cors_allow_credentials,
    allow_methods=_cfg.cors_allow_methods,
    allow_headers=_cfg.cors_allow_headers,
)

# run pre-startup routine
# pre_startup_routine()


@app.on_event("startup")
async def startup_routine() -> None:
    if _cfg.dev_mode:
        # blank line for visual separation of app runs in dev mode
        print(file=sys.stderr)

    # Hello World!
    log.info(
        f"{_cfg.app_name} (TextRig Server v{_cfg.info.version}) "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    init_layer_type_manager()
    setup_routes(app)
    await init_odm(get_db_client(_cfg)[_cfg.db.name])

    # log dev server info for quick browser access
    if _cfg.dev_mode:  # pragma: no cover
        dev_base_url = f"http://{_cfg.uvicorn_host}:{_cfg.uvicorn_port}"
        if _cfg.doc.swaggerui_url:
            log.info(f"\u2022 SwaggerUI docs: {dev_base_url}{_cfg.doc.swaggerui_url}")
        if _cfg.doc.redoc_url:
            log.info(f"\u2022 Redoc API docs: {dev_base_url}{_cfg.doc.redoc_url}")


@app.on_event("shutdown")
async def shutdown_routine() -> None:
    log.info(f"Running {_cfg.info.platform} shutdown sequence")
    if not _cfg.testing:
        get_db_client(_cfg).close()
