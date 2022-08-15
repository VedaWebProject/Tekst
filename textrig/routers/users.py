from fastapi import APIRouter, Depends


router = APIRouter(
    prefix="/users",
    tags=["users"],
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
