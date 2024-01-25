from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from tekst.auth import (
    UserDep,
    UserManager,
    get_user_manager,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# extra endpoint for users to delete their own account
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: UserDep,
    user_mgr: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
) -> None:
    await user_mgr.delete(user, request)
    return None
