from typing import Annotated

from beanie.operators import NE, Eq, Or, Text
from fastapi import APIRouter, Depends, Path, Query, Request, status

from tekst import errors
from tekst.auth import (
    SuperuserDep,
    UserDep,
    UserManager,
    get_user_manager,
)
from tekst.models.common import PydanticObjectId
from tekst.models.search import PaginationSettings
from tekst.models.user import (
    UserDocument,
    UserReadPublic,
    UsersSearchResult,
)
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
    response_model=UsersSearchResult,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def find_users(
    su: SuperuserDep,
    query: Annotated[
        str,
        Query(
            alias="q",
            description="Query string to search in user data",
            max_length=128,
        ),
    ] = "",
    is_active: Annotated[
        bool,
        Query(
            alias="active",
            description="Include active users",
        ),
    ] = True,
    is_inactive: Annotated[
        bool,
        Query(
            alias="inactive",
            description="Include inactive users",
        ),
    ] = True,
    is_verified: Annotated[
        bool,
        Query(
            alias="verified",
            description="Include verified users",
        ),
    ] = True,
    is_unverified: Annotated[
        bool,
        Query(
            alias="unverified",
            description="Include unverified users",
        ),
    ] = True,
    is_superuser: Annotated[
        bool,
        Query(
            alias="admin",
            description="Include administrators",
        ),
    ] = True,
    is_no_superuser: Annotated[
        bool,
        Query(
            alias="user",
            description="Include regular users",
        ),
    ] = True,
    page: Annotated[
        int,
        Query(
            alias="pg",
            description="Page number",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            alias="pgs",
            description="Page size",
        ),
    ] = 10,
) -> UsersSearchResult:
    # construct DB query
    db_query = [
        Text(query) if query else {},
        Or(
            Eq(UserDocument.is_active, is_active),
            NE(UserDocument.is_active, is_inactive),
        ),
        Or(
            Eq(UserDocument.is_verified, is_verified),
            NE(UserDocument.is_verified, is_unverified),
        ),
        Or(
            Eq(UserDocument.is_superuser, is_superuser),
            NE(UserDocument.is_superuser, is_no_superuser),
        ),
    ]

    # count total possible hits
    total = await UserDocument.find(*db_query).count()

    # return actual paginated, sorted restults
    pgn = PaginationSettings(page=page, page_size=page_size)
    return UsersSearchResult(
        users=(
            await UserDocument.find(*db_query)
            .sort(+UserDocument.username)
            .skip(pgn.mongo_skip())
            .limit(pgn.mongo_limit())
            .to_list()
        ),
        total=total,
    )


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
        str,
        val.CleanupOneline,
        Query(
            alias="q",
            description="Query string to search in user data",
            max_length=128,
        ),
    ] = "",
) -> list[UserDocument]:
    """
    Returns a list of public users matching the given query.

    Only returns active user accounts. The query is considered to match a full token
    (e.g. first name, last name, username, a word in the affiliation field).
    """
    if not query:
        return []
    return await UserDocument.find(
        Text(query),
        Eq(UserDocument.is_active, True),
    ).to_list()
