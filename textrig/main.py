from fastapi import Depends, FastAPI
from textrig.config import Config, get_config
from textrig.routers import meta, users


__cfg: Config = get_config()

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
)

app.include_router(users.router)
app.include_router(meta.router)
