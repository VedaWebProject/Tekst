from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from tekst import errors
from tekst.db import get_db_status
from tekst.search import get_es_status


router = APIRouter(
    prefix="/status",
    tags=["status"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=errors.responses([errors.E_503_SERVICE_UNAVAILABLE]),
)
async def api_status(
    db_status: Annotated[dict[str, Any] | None, Depends(get_db_status)],
    es_status: Annotated[dict[str, Any] | None, Depends(get_es_status)],
) -> dict:
    if not db_status or not es_status:  # pragma: no cover
        raise errors.E_503_SERVICE_UNAVAILABLE
    return {
        "status": "Looks good",
    }
