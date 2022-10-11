import textrig.database as db
from fastapi import APIRouter, HTTPException, status
from textrig.models.text import Unit, UnitRead


router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
async def create_unit(unit: Unit) -> dict:

    # find text the unit belongs to
    text = await db.get("texts", unit.text_id)

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The corresponding text does not exist",
        )

    # use all fields but "label" in the example to check for duplicate
    example = {k: v for k, v in unit.dict().items() if k != "label"}
    if await db.get_by_example("texts", example):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The unit conflicts with an existing one",
        )

    return await db.insert(f"{text['slug']}_units", UnitRead(**unit.dict()))
