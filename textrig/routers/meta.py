from fastapi import APIRouter, Depends
from textrig.dependencies import get_token_header
from textrig import __version__

router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("/version")
def read_users():
    return {"version": __version__}