from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Or
from fastapi import APIRouter, Depends, HTTPException, Path, status
from humps import decamelize

from tekst.auth import OptionalUserDep
from tekst.config import TekstConfig
from tekst.dependencies import get_cfg
from tekst.layer_types import layer_type_manager
from tekst.models.platform import PlatformData, PlatformSettingsRead
from tekst.models.settings import PlatformSettingsDocument
from tekst.models.user import User, UserReadPublic
from tekst.routers.texts import get_all_texts


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    responses={404: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=PlatformData,
    summary="Get platform data",
)
async def get_platform_data(
    ou: OptionalUserDep, cfg: Annotated[TekstConfig, Depends(get_cfg)]
) -> dict:
    """Returns data the client needs to initialize"""
    return PlatformData(
        texts=await get_all_texts(ou),
        settings=PlatformSettingsRead.model_from(
            await PlatformSettingsDocument.find_one()
        ),
        layer_types=layer_type_manager.get_layer_types_info(),
    )


@router.get("/user/{usernameOrId}", summary="Get public user info")
async def get_public_user_info(
    username_or_id: Annotated[str | PydanticObjectId, Path(alias="usernameOrId")]
) -> UserReadPublic:
    """Returns public information on the user with the specified username or ID"""
    if PydanticObjectId.is_valid(username_or_id):
        username_or_id = PydanticObjectId(username_or_id)
    user = await User.find_one(
        Or(
            User.id == username_or_id,
            User.username == username_or_id,
        )
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username_or_id}' does not exist",
        )
    return UserReadPublic(
        username=user.username,
        **user.model_dump(
            include={decamelize(field): True for field in user.public_fields}
        ),
    )


@router.get("/i18n", summary="Get server-managed translations")
async def get_translations(lang: str = None) -> dict:
    """Returns server-managed translations."""
    translations = {
        "deDE": {"welcomeTest": '"Willkommen!", sagt der Server!'},
        "enUS": {"welcomeTest": '"Welcome!", says the server!'},
    }
    if lang and lang in translations:
        return translations[lang]
    else:
        return translations
