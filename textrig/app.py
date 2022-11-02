import sys

from fastapi import FastAPI, status
from textrig.config import TextRigConfig, get_config
from textrig.db import indexes
from textrig.db import init_client as init_db_client
from textrig.dependencies import get_db_client
from textrig.logging import log, setup_logging
from textrig.routers import admin, layers, nodes, texts, uidata
from textrig.tags import tags_metadata


# get (possibly cached) config data
_cfg: TextRigConfig = get_config()


def get_app() -> FastAPI:
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
        on_startup=[startup_routine],
        on_shutdown=[shutdown_routine],
        responses={
            status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
        },
    )

    # register routers
    app.include_router(admin.router)
    app.include_router(uidata.router)
    app.include_router(texts.router)
    app.include_router(layers.router)
    app.include_router(nodes.router)

    return app


async def startup_routine() -> None:

    print(file=sys.stderr)  # blank line for visual separation of app runs
    setup_logging()  # set up logging to match prod/dev requirements

    # Hello World!
    log.info(
        f"TextRig Server v{_cfg.info.version} "
        f"running in {'DEVELOPMENT' if _cfg.dev_mode else 'PRODUCTION'} MODE"
    )

    log.info("Initializing database client")
    init_db_client(_cfg.db.get_uri())
    log.info("Creating database indexes")
    await indexes.create_indexes()

    # log dev server info
    if _cfg.dev_mode:
        log.info(
            "Development server bound to "
            f"http://{_cfg.dev_srv_host}:{_cfg.dev_srv_port}"
        )


async def shutdown_routine():

    log.info("Closing database client")
    get_db_client(_cfg).close()


app = get_app()
