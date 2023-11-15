from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Or
from fastapi import APIRouter, Depends, HTTPException, Path, status
from humps import decamelize

from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.config import TekstConfig
from tekst.dependencies import get_cfg
from tekst.layer_types import layer_type_manager
from tekst.models.platform import PlatformData
from tekst.models.segment import (
    ClientSegmentCreate,
    ClientSegmentDocument,
    ClientSegmentHead,
    ClientSegmentRead,
    ClientSegmentUpdate,
)
from tekst.models.settings import (
    PlatformSettingsDocument,
    PlatformSettingsRead,
    PlatformSettingsUpdate,
)
from tekst.models.user import UserDocument, UserReadPublic
from tekst.routers.texts import get_all_texts
from tekst.settings import get_settings


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
        settings=await get_settings(),
        layer_types=layer_type_manager.get_layer_types_info(),
        system_segments=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == True  # noqa: E712
        ).to_list(),
        pages_info=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == False  # noqa: E712
        )
        .project(ClientSegmentHead)
        .to_list(),
    )


@router.get("/user/{usernameOrId}", summary="Get public user info")
async def get_public_user_info(
    username_or_id: Annotated[str | PydanticObjectId, Path(alias="usernameOrId")]
) -> UserReadPublic:
    """Returns public information on the user with the specified username or ID"""
    if PydanticObjectId.is_valid(username_or_id):
        username_or_id = PydanticObjectId(username_or_id)
    user = await UserDocument.find_one(
        Or(
            UserDocument.id == username_or_id,
            UserDocument.username == username_or_id,
        )
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username_or_id}' does not exist",
        )
    return dict(
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


@router.patch(
    "/settings", response_model=PlatformSettingsRead, status_code=status.HTTP_200_OK
)
async def update_platform_settings(
    su: SuperuserDep,
    updates: PlatformSettingsUpdate,
) -> PlatformSettingsRead:
    settings_doc = await PlatformSettingsDocument.find_one()
    if not settings_doc:
        await get_settings(force_nocache=True)
        settings_doc = await PlatformSettingsDocument.find_one()
    await settings_doc.apply(updates.model_dump(exclude_unset=True))
    return settings_doc


@router.get(
    "/segments/{id}",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_200_OK,
)
async def get_segment(
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> ClientSegmentDocument:
    segment = await ClientSegmentDocument.get(segment_id)
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client segment with ID {segment_id} doesn't exist",
        )
    return segment


@router.post(
    "/segments", response_model=ClientSegmentRead, status_code=status.HTTP_201_CREATED
)
async def create_segment(
    su: SuperuserDep,
    segment: ClientSegmentCreate,
) -> ClientSegmentDocument:
    if await ClientSegmentDocument.find_one(
        ClientSegmentDocument.key == segment.key,
        ClientSegmentDocument.locale == segment.locale,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An equal segment already exists (same key and locale)",
        )
    return await ClientSegmentDocument.model_from(segment).create()


@router.patch(
    "/segments/{id}", response_model=ClientSegmentRead, status_code=status.HTTP_200_OK
)
async def update_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: ClientSegmentUpdate,
) -> ClientSegmentDocument:
    segment_doc = await ClientSegmentDocument.get(segment_id)
    if not segment_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client segment {segment_doc} doesn't exist",
        )
    await segment_doc.apply(updates.model_dump(exclude_unset=True))
    return segment_doc


@router.delete("/segments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    if not await ClientSegmentDocument.find_one(
        ClientSegmentDocument.id == segment_id
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client segment {segment_id} doesn't exist",
        )
    if not (
        await ClientSegmentDocument.find_one(
            ClientSegmentDocument.id == segment_id
        ).delete()
    ).acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong deleting the segment",
        )
