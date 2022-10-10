import textrig.database as db
from fastapi import APIRouter, HTTPException, status
from textrig.models.text import TextRead


router = APIRouter(
    prefix="/text",
    tags=["text"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/all", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextRead]:
    return await db.get_all("texts", limit=limit)


@router.get("/get/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str) -> dict:
    text = await db.get("texts", text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A text with the given ID cannot be found",
        )
    return text
