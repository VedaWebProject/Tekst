import textrig.database as db
from fastapi import APIRouter, HTTPException, status
from pymongo.results import InsertOneResult
from textrig.models.user import User, UserCreate, UserUpdate


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/create", response_model=User | dict, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    if await db.users.find_one({"username": user.username}):
        return {"foo": "bar"}
    result: InsertOneResult = await db.users.insert_one(user.dict())
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user",
        )
    return User(**await db.users.find_one({"_id": result.inserted_id}))


@router.patch("/update/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user_update: UserUpdate):
    if not await db.update("users", user_id, user_update):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update user {user_id}",
        )
    user_data = await db.get("users", user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not return user data for {user_id}",
        )
    return User(**user_data)
