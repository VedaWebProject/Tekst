from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig, get_config


router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("", summary="Platform metadata")
async def meta(config: TextRigConfig = Depends(get_config)):
    """
    Returns platform metadata, possibly customized for this platform instance.
    """
    return {
        "title": f"{config.app_name}{' (dev mode)' if config.dev_mode else ''}",
        "description": config.info.description,
        "website": config.info.website,
        "platform": config.info.platform,
        "platform_website": config.info.platform_website,
        "version": config.info.version,
        "license": config.info.license,
        "license_url": config.info.license_url,
    }
