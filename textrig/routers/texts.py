import json

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, status
from textrig.config import TextRigConfig, get_config
from textrig.dependencies import get_cfg
from textrig.logging import log
from textrig.models.text import TextCreate, TextDocument, TextRead, TextUpdate
from textrig.utils import importer


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextRead]:
    return await TextDocument.find_all(limit=limit).project(TextRead).to_list()


@router.post("", response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(text: TextCreate) -> TextRead:
    if await TextDocument.find_one(
        TextDocument.title == text.title, TextDocument.slug == text.slug
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An equal text already exists (same title or slug)",
        )
    return await TextDocument.from_(text).create()


@router.post(
    "/import",
    response_model=TextRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=_cfg.dev_mode,
)
async def import_text(
    file: UploadFile,
    cfg: TextRigConfig = Depends(get_cfg),
) -> TextRead:  # pragma: no cover
    if not cfg.dev_mode:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Endpoint not available in production system",
        )

    log.debug(f'Importing text data from uploaded file "{file.filename}" ...')

    try:
        text = await importer.import_text(json.loads(await file.read()))
    except HTTPException as e:
        log.error(e.detail)
        raise e
    except Exception as e:
        log.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid import data: {str(e)}",
        )
    finally:
        await file.close()

    return text


@router.get("/{textId}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text(text_id: PydanticObjectId = Path(..., alias="textId")) -> TextRead:
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )
    return text


@router.patch("/{textId}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def update_text(
    updates: TextUpdate, text_id: PydanticObjectId = Path(..., alias="textId")
) -> dict:
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text with ID {text_id} doesn't exist",
        )
    if updates.slug and updates.slug != text.slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text slug cannot be changed",
        )
    await text.set(updates.dict(exclude_unset=True))
    return text
