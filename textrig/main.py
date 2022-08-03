from fastapi import Depends, FastAPI
from textrig import __version__
from textrig.config import Config, get_config

from .routers import users, meta


# app = FastAPI(root_path="/api")
app = FastAPI()

app.include_router(users.router)
app.include_router(meta.router)


@app.get("/")
def root(config: Config = Depends(get_config)):
    return {
        "platform": config.app_name,
        "system": "TextRig Server",
        "version": __version__
    }
