from typing import Union

from fastapi import FastAPI
from textrig import __version__

app = FastAPI()


@app.get("/")
def hello_world():
    return {"app": "TextRig Server", "version": __version__}
