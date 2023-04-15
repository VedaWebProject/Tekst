from typing import Any

from fastapi import APIRouter, Depends, status

from tekst.auth import SuperuserDep
from tekst.config import TekstConfig, get_config


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
async def hello_admin(su: SuperuserDep, cfg: TekstConfig = Depends(get_config)) -> dict:
    return {
        "message": (
            "Welcome, Admin! This is "
            f"{cfg.tekst_info.name} v{cfg.tekst_info.version}!"
        )
    }
