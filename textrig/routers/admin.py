import json

import textrig.database as db
from fastapi import APIRouter, HTTPException, UploadFile, status
from textrig.models.text import Text, TextInDB, TextUpdate, Unit, UnitInDB


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post(
    "/text/create", response_model=TextInDB, status_code=status.HTTP_201_CREATED
)
async def create_text(text: Text) -> TextInDB:
    if await db.get("texts", text.slug, "slug"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A text with an equal title already exists",
        )
    return TextInDB(
        **await db.insert("texts", TextInDB(**text.dict(exclude_unset=True)))
    )


@router.post(
    "/text/import-sample-data", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def import_text(file: UploadFile) -> dict:
    try:
        # parse data
        data = json.loads(await file.read())
        # import data
        for text in data.get("texts", []):
            await db.insert("texts", TextInDB(**text))
        for unit in data.get("units", []):
            await db.insert("units", UnitInDB(**unit))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid import data: {str(e)}",
        )
    finally:
        await file.close()
    # OK
    return {"status": "done"}


@router.post(
    "/unit/create", response_model=UnitInDB, status_code=status.HTTP_201_CREATED
)
async def create_unit(unit: Unit) -> UnitInDB:
    # find text the unit belongs to
    text = await db.get("texts", unit.text)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The corresponding text does not exist",
        )
    # use all fields but "label" in the example to check for duplicate
    example = {k: v for k, v in unit.dict(exclude_unset=True).items() if k != "label"}
    if await db.get_by_example("texts", example):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The unit conflicts with an existing one",
        )
    return UnitInDB(
        **await db.insert(
            f"{text['slug']}_units", UnitInDB(**unit.dict(exclude_unset=True))
        )
    )


@router.patch(
    "/text/update/{text_id}", response_model=TextInDB, status_code=status.HTTP_200_OK
)
async def update_text(text_id: str, text_update: TextUpdate):
    if not await db.update("texts", text_id, text_update):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update text {text_id}",
        )
    text_data = await db.get("texts", text_id)
    if not text_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not return data for text {text_id}",
        )
    return TextInDB(**text_data)
