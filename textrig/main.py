from fastapi import FastAPI
from textrig import __version__

app = FastAPI()


@app.get("/version")
def version():
    return {"version": __version__}
