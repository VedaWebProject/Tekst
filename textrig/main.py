from fastapi import Depends, FastAPI
from textrig import __version__
from textrig.config import Config, get_config


# app = FastAPI(root_path="/api")
app = FastAPI()


@app.get("/version")
def version():
    return {"version": __version__}


@app.get("/config")
def config(config: Config = Depends(get_config)):
    return config.dict()
