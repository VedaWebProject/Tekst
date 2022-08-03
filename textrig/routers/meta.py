from fastapi import APIRouter, Depends
from textrig.dependencies import get_token_header
from textrig import pkg_meta

router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("/version")
def read_users():
    return {"version": pkg_meta["version"]}