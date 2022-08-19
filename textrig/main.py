from fastapi import FastAPI
from textrig.config import TextRigConfig, get_config
from textrig.routers import meta, user


# get (possibly cached) config data
_cfg: TextRigConfig = get_config()

# define tags metadata for API documentation
# TODO: This should go elsewhere...
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
        "externalDocs": {
            "description": "Users external docs",
            "url": "https://vedaweb.uni-koeln.de",
        },
    },
]

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
app.include_router(user.router)
app.include_router(meta.router)
