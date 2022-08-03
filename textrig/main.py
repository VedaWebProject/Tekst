from fastapi import Depends, FastAPI
from textrig.config import Config, get_config
from textrig.routers import meta, users


# get (possibly cached) config data
__cfg: Config = get_config()

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
    root_path=__cfg.root_path,
    title=__cfg.app_name,
    description=__cfg.description,
    version=__cfg.version,
    terms_of_service=__cfg.terms,
    contact={
        "name": __cfg.contact_name,
        "url": __cfg.contact_url,
        "email": __cfg.contact_email,
    },
    license_info={
        "name": __cfg.license,
        "url": __cfg.license_url,
    },
    openapi_tags=tags_metadata
)

# register routers
app.include_router(users.router)
app.include_router(meta.router)
