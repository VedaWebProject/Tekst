from fastapi import APIRouter, HTTPException, status
from textrig.db import crud
from textrig.models.text import Text, TextRead, TextUpdate


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextRead]:
    return await crud.get_many("texts", limit=limit)


@router.post("", response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(text: Text) -> dict:

    if await crud.get("texts", text.slug, "slug"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A text with an equal slug already exists",
        )

    return await crud.insert("texts", text)


@router.get("/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str) -> dict:
    text = await crud.get("texts", text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A text with the given ID cannot be found",
        )
    return text


@router.patch("/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def update_text(text_id: str, text_update: TextUpdate) -> dict:

    if not await crud.update("texts", text_id, text_update):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update text {text_id}",
        )

    text_data = await crud.get("texts", text_id)

    if not text_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not return data for text {text_id}",
        )

    return text_data
