from fastapi import APIRouter, Depends
from textrig.dependencies import get_token_header


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/me")
def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/{username}")
def read_user(username: str):
    return {"username": username}
