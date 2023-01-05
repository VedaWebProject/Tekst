import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from textrig.config import TextRigConfig, get_config
from textrig.db.io import DbIO
from textrig.dependencies import get_cfg, get_db_io
from textrig.logging import log
from textrig.models.text import Text, TextRead, TextUpdate
from textrig.utils import importer


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(
    db_io: DbIO = Depends(get_db_io), limit: int = 100
) -> list[TextRead]:
    return await db_io.find("texts", limit=limit)


@router.post("", response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(text: Text, db_io: DbIO = Depends(get_db_io)) -> TextRead:
    return await text.create(db_io)


@router.post(
    "/import",
    response_model=TextRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=_cfg.dev_mode,
)
async def import_text(
    file: UploadFile,
    cfg: TextRigConfig = Depends(get_cfg),
    db_io: DbIO = Depends(get_db_io),
) -> TextRead:  # pragma: no cover
    if not cfg.dev_mode:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Endpoint not available in production system",
        )

    log.debug(f'Importing text data from uploaded file "{file.filename}" ...')

    try:
        text = await importer.import_text(json.loads(await file.read()), db_io)
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


@router.get("/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str, db_io: DbIO = Depends(get_db_io)) -> dict:
    return await TextRead.read(text_id, db_io)


@router.patch("", response_model=TextRead, status_code=status.HTTP_200_OK)
async def update_text(
    text_update: TextUpdate, db_io: DbIO = Depends(get_db_io)
) -> dict:
    return await text_update.update(db_io)
