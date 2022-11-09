from typing import Any

from fastapi import APIRouter, Depends
from textrig.config import TextRigConfig, get_config


router = APIRouter(
    prefix="/uidata",
    tags=["uidata"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=dict[str, Any],
    summary="Data the client needs to display in the UI",
)
async def uidata(cfg: TextRigConfig = Depends(get_config)) -> dict:
    """Returns all UI data at once"""
    return {
        "platform": await uidata_platform(cfg),
        "help": await uidata_help(),
    }


@router.get("/platform", response_model=dict[str, str], summary="Platform metadata")
async def uidata_platform(cfg: TextRigConfig = Depends(get_config)) -> dict:
    """Returns platform metadata, possibly customized for this platform instance."""
    return dict(title=cfg.app_name, **cfg.info.dict())


@router.get("/help", response_model=dict[str, str], summary="Help texts")
async def uidata_help() -> dict:
    """Returns all help texts."""
    # TODO: Load help texts from Markdown source
    return {
        "foo": "foo",
        "bar": "bar",
        "baz": "baz",
    }
