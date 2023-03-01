from typing import Any

from fastapi import APIRouter, Depends, status

from textrig.config import TextRigConfig, get_config


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
async def hello_admin(cfg: TextRigConfig = Depends(get_config)) -> dict:
    return {
        "message": (
            "Welcome, Admin! This is "
            f"{cfg.textrig_info.name} v{cfg.textrig_info.version}!"
        )
    }
