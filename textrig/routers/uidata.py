from typing import Any

from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig, get_config


router = APIRouter(
    prefix="/uidata",
    tags=["uidata"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=dict[str, Any], summary="Platform metadata")
async def meta(cfg: TextRigConfig = Depends(get_config)) -> dict:
    """
    Returns all UI data at once
    """
    return {
        "platform": await uidata_platform(cfg),
    }


@router.get("/platform", response_model=dict[str, str], summary="Platform metadata")
async def uidata_platform(cfg: TextRigConfig = Depends(get_config)) -> dict:
    """
    Returns platform metadata, possibly customized for this platform instance.
    """
    return {
        "title": f"{cfg.app_name}{' (dev mode)' if cfg.dev_mode else ''}",
        "description": cfg.info.description,
        "website": cfg.info.website,
        "platform": cfg.info.platform,
        "platform_website": cfg.info.platform_website,
        "version": cfg.info.version,
        "license": cfg.info.license,
        "license_url": cfg.info.license_url,
    }
