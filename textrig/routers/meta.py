from fastapi import APIRouter, Depends
from textrig.config import Config, get_config
from textrig.dependencies import get_token_header


router = APIRouter(
    prefix="/meta",
    tags=["meta"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def meta(config: Config = Depends(get_config)):
    return {
        "title": config.app_name,
        "description": config.description,
        "website": config.website,
        "platform": config.platform,
        "platform_website": config.platform_website,
        "version": config.version,
        "license": config.license,
        "license_url": config.license_url,
    }
