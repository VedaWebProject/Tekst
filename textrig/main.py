from fastapi import FastAPI
from textrig import database as db
from textrig.config import TextRigConfig, get_config
from textrig.routers import admin, meta, text
from textrig.tags import tags_metadata


# get (possibly cached) config data
_cfg: TextRigConfig = get_config()


# create app instance
app = FastAPI(
    root_path="" if _cfg.dev_mode else _cfg.root_path,
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
)


# register routers
app.include_router(admin.router)
app.include_router(meta.router)
app.include_router(text.router)


# initialize things
@app.on_event("startup")
async def on_startup():
    await db.init()
