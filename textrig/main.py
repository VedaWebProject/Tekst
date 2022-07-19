from fastapi import Depends, FastAPI
from textrig import __version__

from .settings import Settings, get_settings

app = FastAPI(root_path="/api")


@app.get("/version")
def version():
    return {"version": __version__}


@app.get("/settings")
def settings(settings: Settings = Depends(get_settings)):
    return settings.dict()
