from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Path, status

from tekst import errors
from tekst.auth import SuperuserDep
from tekst.models.notice import NoticeCreate, NoticeDocument, NoticeRead


router = APIRouter(
    prefix="/notices",
    tags=["notices"],
)


@router.post(
    "",
    response_model=NoticeRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_notice(
    notice: NoticeCreate,
    user: SuperuserDep,
) -> NoticeDocument:
    """Creates a platform notice"""
    return await NoticeDocument.model_from(notice).create()


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_NOT_FOUND,
        ]
    ),
)
async def delete_notice(
    notice_id: Annotated[PydanticObjectId, Path(alias="id")],
    user: SuperuserDep,
) -> None:
    """Deletes a specific platform notice"""
    notice_doc = await NoticeDocument.get(notice_id)
    if not notice_doc:
        raise errors.E_404_NOT_FOUND
    await notice_doc.delete()


@router.patch(
    "/{id}",
    response_model=NoticeRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_NOT_FOUND,
        ]
    ),
)
async def update_notice(
    notice_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: NoticeCreate,
    user: SuperuserDep,
) -> NoticeDocument:
    """Updates a specific platform notice"""
    notice_doc = await NoticeDocument.get(notice_id)
    if not notice_doc:
        raise errors.E_404_NOT_FOUND
    await notice_doc.apply_updates(updates)
    return notice_doc
