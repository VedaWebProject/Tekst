from fastapi import APIRouter, Depends
from textrig.config import Config, get_config


router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", summary="Platform metadata")
def meta(config: Config = Depends(get_config)):
    """
    Returns platform metadata, possibly customized for this platform instance.
    """
    return {
        "title": f"{config.app_name}{' (dev mode)' if config.dev_mode else ''}",
        "description": config.description,
        "website": config.website,
        "platform": config.platform,
        "platform_website": config.platform_website,
        "version": config.version,
        "license": config.license,
        "license_url": config.license_url,
    }
