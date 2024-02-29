from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import NotIn, Or, Text
from fastapi import APIRouter, Path, Query, status

from tekst import errors
from tekst.auth import (
    OptionalUserDep,
    SuperuserDep,
    UserDep,
)
from tekst.config import ConfigDep
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
from tekst.utils import validators as val


router = APIRouter(
    prefix="/platform",
    tags=["platform"],
)


# ROUTES DEFINITIONS...


@router.get(
    "",
    response_model=PlatformData,
    summary="Get platform data",
    status_code=status.HTTP_200_OK,
)
async def get_platform_data(ou: OptionalUserDep, cfg: ConfigDep) -> dict:
    """Returns data the client needs to initialize"""
    return PlatformData(
        texts=await get_all_texts(ou),
        settings=await get_settings(),
        system_segments=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == True  # noqa: E712
        ).to_list(),
        info_segments=await ClientSegmentDocument.find(
            ClientSegmentDocument.is_system_segment == False  # noqa: E712
        )
        .project(ClientSegmentHead)
        .to_list(),
    )


@router.get(
    "/users/{user}",
    response_model=UserReadPublic,
    summary="Get public user info",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_USER_NOT_FOUND,
        ]
    ),
)
async def get_public_user(
    username_or_id: Annotated[
        str | PydanticObjectId, Path(alias="user", description="Username or ID")
    ],
) -> dict:
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
        raise errors.E_404_USER_NOT_FOUND
    return UserReadPublic(**user.model_dump())


@router.get(
    "/users",
    response_model=list[UserReadPublic],
    status_code=status.HTTP_200_OK,
)
async def find_public_users(
    su: UserDep,
    query: Annotated[
        str | None,
        val.CleanupOneline,
        val.EmptyStringToNone,
        Query(alias="q", description="Query string to search in user data"),
    ] = None,
) -> list[UserDocument]:
    """
    Returns a list of public users matching the given query.

    Only returns active user accounts. The query is considered to match a full token
    (e.g. first name, last name, username, a word in the affiliation field).
    """
    if not query:
        return []
    return [
        UserReadPublic(**user.model_dump())
        for user in await UserDocument.find(Text(query)).to_list()
        if user.is_active
    ]


@router.patch(
    "/settings",
    response_model=PlatformSettingsRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_platform_settings(
    su: SuperuserDep,
    updates: PlatformSettingsUpdate,
) -> PlatformSettingsDocument:
    # reset user locales if the update reduces available locales
    if updates.available_locales and isinstance(updates.available_locales, list):
        await UserDocument.find(
            NotIn(UserDocument.locale, updates.available_locales + [None])
        ).set(
            {
                UserDocument.locale: "enUS"
                if "enUS" in updates.available_locales
                else updates.available_locales[0]
            }
        )
    # apply updates
    settings_doc = await get_settings()
    return await settings_doc.apply_updates(updates)


@router.get(
    "/segments/{id}",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
        ]
    ),
)
async def get_segment(
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> ClientSegmentDocument:
    segment = await ClientSegmentDocument.get(segment_id)
    if not segment:
        raise errors.E_404_SEGMENT_NOT_FOUND
    return segment


@router.post(
    "/segments",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_SEGMENT_KEY_LOCALE_CONFLICT,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_segment(
    su: SuperuserDep,
    segment: ClientSegmentCreate,
) -> ClientSegmentDocument:
    if await ClientSegmentDocument.find_one(
        ClientSegmentDocument.key == segment.key,
        ClientSegmentDocument.locale == segment.locale,
    ).exists():
        raise errors.E_409_SEGMENT_KEY_LOCALE_CONFLICT
    return await ClientSegmentDocument.model_from(segment).create()


@router.patch(
    "/segments/{id}",
    response_model=ClientSegmentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: ClientSegmentUpdate,
) -> ClientSegmentDocument:
    segment_doc = await ClientSegmentDocument.get(segment_id)
    if not segment_doc:
        raise errors.E_404_SEGMENT_NOT_FOUND
    return await segment_doc.apply_updates(updates)


@router.delete(
    "/segments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_SEGMENT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_segment(
    su: SuperuserDep,
    segment_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    if not await ClientSegmentDocument.find_one(
        ClientSegmentDocument.id == segment_id
    ).exists():
        raise errors.E_404_SEGMENT_NOT_FOUND
    delete_result = await ClientSegmentDocument.find_one(
        ClientSegmentDocument.id == segment_id
    ).delete()
    if (
        not delete_result.acknowledged or not delete_result.deleted_count
    ):  # pragma: no cover
        raise errors.E_500_INTERNAL_SERVER_ERROR
