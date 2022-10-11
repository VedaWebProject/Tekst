import json
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, status
from textrig.config import TextRigConfig, get_config
from textrig.db import crud
from textrig.logging import log
from textrig.models.text import TextRead, UnitRead


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post(
    "/import-sample-data",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=_cfg.dev_mode,
)
async def import_text(file: UploadFile) -> dict:

    if not _cfg.dev_mode:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Endpoint not available in production system",
        )

    try:
        # parse data
        data = json.loads(await file.read())
        log.debug(f"Parsed sample data import: {list(data.keys())}")
        texts = [TextRead(**td) for td in data.get("texts", [])]
        units = [UnitRead(**ud) for ud in data.get("units", [])]
        result = dict(
            texts=await crud.insert_many("texts", texts),
            units=await crud.insert_many("units", units),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid import data: {str(e)}",
        )
    finally:
        await file.close()

    return result
