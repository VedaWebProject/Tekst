import json

from fastapi import APIRouter, HTTPException, status, UploadFile, Depends
from textrig.config import TextRigConfig, get_config
from textrig.dependencies import get_cfg
from textrig.utils.validators import validate_id

from textrig.logging import log
from textrig.models.text import Text, TextUpdate


from textrig.utils import importer


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[Text], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[Text]:
    return await Text.find_all(limit=limit).to_list()


@router.post("", response_model=Text, status_code=status.HTTP_201_CREATED)
async def create_text(text: Text) -> Text:
    if await Text.find_one(Text.slug == text.slug):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An equal text already exists (same slug)",
        )
    return await text.create()


@router.post(
    "/import",
    response_model=Text,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=_cfg.dev_mode,
)
async def import_text(
    file: UploadFile,
    cfg: TextRigConfig = Depends(get_cfg),
) -> Text:  # pragma: no cover
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


@router.get("/{text_id}", response_model=Text, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str) -> dict:
    validate_id(text_id)
    text = await Text.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )
    return text


@router.patch("", response_model=Text, status_code=status.HTTP_200_OK)
async def update_text(text_update: TextUpdate) -> dict:
    text: Text = await Text.get(text_update.id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text with ID {text_update.id} doesn't exist",
        )
    if text_update.slug and text_update.slug != text.slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text slug cannot be changed",
        )
    await text.set(text_update.dict())
    return text
