import textrig.database as db
from fastapi import APIRouter, HTTPException, status
from textrig.models.text import TextInDB


router = APIRouter(
    prefix="/text",
    tags=["text"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/all", response_model=list[TextInDB], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextInDB]:
    return await db.get_all("texts", limit=limit)


@router.get("/get/{text_id}", response_model=TextInDB, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str) -> TextInDB:
    text = await db.get("texts", text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A text with the given ID cannot be found",
        )
    return text
