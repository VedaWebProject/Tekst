from fastapi import HTTPException, status
from beanie import PydanticObjectId


def validate_id(id_: str) -> None:
    try:
        PydanticObjectId(id_)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID {id_}",
        )
