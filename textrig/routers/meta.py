from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig, get_config


router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("", summary="Platform metadata")
async def meta(cfg: TextRigConfig = Depends(get_config)):
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
