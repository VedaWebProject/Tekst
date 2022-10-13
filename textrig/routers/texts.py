import json

from fastapi import APIRouter, HTTPException, UploadFile, status
from textrig.config import TextRigConfig, get_config
from textrig.db import crud
from textrig.logging import log
from textrig.models.text import Text, TextRead, TextUpdate, Unit, UnitRead
from textrig.routers.units import create_unit


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/texts", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextRead]:
    return await crud.find("texts", limit=limit)


@router.post("/texts", response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(text: Text) -> dict:

    if await crud.find_one("texts", text.slug, "slug"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A text with an equal slug already exists",
        )

    text = await crud.insert_one("texts", text)
    log.debug(f"Created text: {text}")
    return text


@router.post(
    "/texts/import",
    response_model=TextRead,
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
        log.debug(f'Importing text data from uploaded file "{file.filename}"')

        # create and save text object
        text: TextRead = TextRead(**await create_text(Text(**data)))

        # process text structure
        from collections import deque

        stack = deque()
        indices = [0]

        # push units of first structure level onto stack
        for unit in data.get("structure", []):
            unit["parentId"] = None
            unit["textSlug"] = text.slug
            unit["level"] = 0
            unit["index"] = indices[0]
            stack.append(unit)
            indices[0] += 1

        # process stack
        while stack:
            unit_data = stack.pop()
            unit: UnitRead = UnitRead(**await create_unit(Unit(**unit_data)))

            for u in unit_data.get("units", []):
                u["parentId"] = unit.id
                u["textSlug"] = text.slug
                u["level"] = unit.level + 1
                if len(indices) <= u["level"]:
                    indices.append(0)
                u["index"] = indices[u["level"]]
                indices[u["level"]] += 1
                stack.append(u)

        return text

    except Exception as e:
        log.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid import data: {str(e)}",
        )
    finally:
        await file.close()


@router.get("/texts/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text_by_id(text_id: str) -> dict:
    text = await crud.find_one("texts", text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A text with the given ID cannot be found",
        )
    return text


@router.patch(
    "/texts/{text_id}", response_model=TextRead, status_code=status.HTTP_200_OK
)
async def update_text(text_id: str, text_update: TextUpdate) -> dict:

    if not await crud.update("texts", text_id, text_update):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update text {text_id}",
        )

    text_data = await crud.find_one("texts", text_id)

    if not text_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not return data for text {text_id}",
        )

    return text_data
