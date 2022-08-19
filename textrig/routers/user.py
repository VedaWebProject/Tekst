from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.results import InsertOneResult
from textrig.database import Database, get_db
from textrig.models.user import User, UserCreate, UserUpdate


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/create", response_model=User | dict, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Database = Depends(get_db)):
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
async def update_user(
    user_id: str, user_update: UserUpdate, db: Database = Depends(get_db)
):
    result = await db.users.update_one(
        filter={"_id": ObjectId(user_id)},
        update={"$set": user_update.dict(exclude_unset=True)},
    )
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user",
        )
    return User(**await db.users.find_one({"_id": ObjectId(user_id)}))
