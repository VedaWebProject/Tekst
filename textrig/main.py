from fastapi import Depends, FastAPI
from textrig.config import Config, get_config
from textrig.routers import meta, users


# get (possibly cached) config data
_cfg: Config = get_config()

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
    description=_cfg.description,
    version=_cfg.version,
    terms_of_service=_cfg.terms,
    contact={
        "name": _cfg.contact_name,
        "url": _cfg.contact_url,
        "email": _cfg.contact_email,
    },
    license_info={
        "name": _cfg.license,
        "url": _cfg.license_url,
    },
    openapi_tags=tags_metadata,
    openapi_url=_cfg.openapi_url,
    docs_url=_cfg.swaggerui_url,
    redoc_url=_cfg.redoc_url,
)

# register routers
app.include_router(users.router)
app.include_router(meta.router)
