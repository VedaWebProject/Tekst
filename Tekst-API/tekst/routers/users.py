from typing import Annotated

from beanie.operators import Or, Text
from fastapi import APIRouter, Depends, Path, Query, Request, status

from tekst import errors
from tekst.auth import (
    SuperuserDep,
    UserDep,
    UserManager,
    get_user_manager,
)
from tekst.models.common import PydanticObjectId
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.utils import validators as val


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# extra endpoint for users to delete their own account
@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
)
async def delete_me(
    user: UserDep,
    user_mgr: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
) -> None:
    await user_mgr.delete(user, request)
    return None


@router.get(
    "",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_users(su: SuperuserDep) -> list[UserDocument]:
    return await UserDocument.find_all().to_list()


@router.get(
    "/public/{user}",
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
    "/public",
    response_model=list[UserReadPublic],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
        ]
    ),
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
