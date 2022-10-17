from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.models.text import Unit, UnitRead


router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
async def create_unit(unit: Unit, db_io: DbIO = Depends(get_db_io)) -> dict:

    # find text the unit belongs to
    text = await db_io.find_one("texts", unit.text_slug, field="slug")

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The corresponding text does not exist",
        )

    # use all fields but "label" in the example to check for duplicate
    example = {k: v for k, v in unit.dict().items() if k != "label"}
    if await db_io.find_one_by_example("texts", example):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The unit conflicts with an existing one",
        )

    return await db_io.insert_one("units", unit)


@router.get("", response_model=list[UnitRead], status_code=status.HTTP_200_OK)
async def get_units(
    text_slug: str,
    level: int,
    index: int = None,
    parent_id: str = None,
    limit: int = 1000,
    db_io: DbIO = Depends(get_db_io),
) -> list:

    example = dict(text_slug=text_slug, level=level)

    if index is not None:
        example["index"] = index

    if parent_id:
        example["parent_id"] = ObjectId(parent_id)

    return await db_io.find("units", example=example, limit=limit)
