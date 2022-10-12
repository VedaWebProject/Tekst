from fastapi import APIRouter, status


# from textrig.config import TextRigConfig, get_config


# _cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)
