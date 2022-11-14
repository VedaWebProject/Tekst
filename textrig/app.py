import sys

from fastapi import FastAPI, status
from textrig.config import TextRigConfig, get_config
from textrig.db import indexes
from textrig.db import init_client as init_db_client
from textrig.dependencies import get_db_client
from textrig.layer_types import init_layer_type_manager
from textrig.logging import log, setup_logging
from textrig.routers import admin, layer, node, text, uidata, unit
from textrig.tags import tags_metadata


# get (possibly cached) config data
_cfg: TextRigConfig = get_config()


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


# register routers  # TODO: do that dynamically!
app.include_router(admin.router)
app.include_router(uidata.router)
app.include_router(text.router)
app.include_router(layer.router)
app.include_router(node.router)


@app.on_event("startup")
async def startup_routine() -> None:
    print(file=sys.stderr)  # blank line for visual separation of app runs
    setup_logging()  # set up logging to match prod/dev requirements

    # Hello World!
    log.info(
        f"TextRig Server v{_cfg.info.version} "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    init_layer_type_manager()
    app.include_router(unit.get_router())

    log.info("Initializing database client")
    init_db_client(_cfg.db.get_uri())

    log.info("Creating database indexes")
    await indexes.create_indexes()

    # log dev server info
    if _cfg.dev_mode:  # pragma: no cover
        log.info(
            "Development server bound to "
            f"http://{_cfg.dev_srv_host}:{_cfg.dev_srv_port}"
        )


@app.on_event("shutdown")
async def shutdown_routine() -> None:
    log.info("Closing database client")
    get_db_client(_cfg).close()
