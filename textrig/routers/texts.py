import textrig.database as db
from fastapi import APIRouter, HTTPException, status
from textrig.models.text import Text, TextCreate, TextUpdate


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/create", response_model=Text, status_code=status.HTTP_201_CREATED)
async def create_text(text: TextCreate):
    if await db.get("texts", text.safe_title, "safe_title"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A text with an equal title already exists",
        )
    return Text(**await db.insert("texts", Text(**text.dict(exclude_unset=True))))


@router.patch("/update/{text_id}", response_model=Text, status_code=status.HTTP_200_OK)
async def update_text(text_id: str, text_update: TextUpdate):
    if not await db.update("texts", text_id, text_update):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update text {text_id}",
        )
    text_data = await db.get("texts", text_id)
    print(text_data)
    if not text_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not return data for text {text_id}",
        )
    return Text(**text_data)
