from typing import Annotated

from fastapi import APIRouter, Path, status

from tekst import errors
from tekst.auth import (
    UserDep,
)
from tekst.models.bookmark import BookmarkCreate, BookmarkDocument, BookmarkRead
from tekst.models.common import PydanticObjectId
from tekst.models.location import LocationDocument
from tekst.models.text import TextDocument


router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_BOOKMARK_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_bookmark(
    user: UserDep,
    bookmark_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    bookmark_doc = await BookmarkDocument.get(bookmark_id)
    if not bookmark_doc:
        raise errors.E_404_BOOKMARK_NOT_FOUND
    if user.id != bookmark_doc.user_id:
        raise errors.E_403_FORBIDDEN
    await bookmark_doc.delete()


@router.get(
    "",
    response_model=list[BookmarkRead],
    status_code=status.HTTP_200_OK,
)
async def get_user_bookmarks(user: UserDep) -> list[BookmarkDocument]:
    """Returns all bookmarks that belong to the requesting user"""
    return (
        await BookmarkDocument.find(BookmarkDocument.user_id == user.id)
        .sort(
            +BookmarkDocument.text_id,
            +BookmarkDocument.level,
            +BookmarkDocument.position,
        )
        .to_list()
    )


@router.post(
    "",
    response_model=BookmarkRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_BOOKMARK_EXISTS,
            errors.E_409_BOOKMARKS_LIMIT_REACHED,
            errors.E_404_LOCATION_NOT_FOUND,
            errors.E_404_TEXT_NOT_FOUND,
        ]
    ),
)
async def create_bookmark(user: UserDep, bookmark: BookmarkCreate) -> BookmarkDocument:
    """Creates a bookmark for the requesting user"""

    if await BookmarkDocument.find(
        BookmarkDocument.user_id == user.id,
        BookmarkDocument.location_id == bookmark.location_id,
    ).exists():
        raise errors.E_409_BOOKMARK_EXISTS

    if (
        await BookmarkDocument.find(BookmarkDocument.user_id == user.id).count()
    ) >= 1000:
        raise errors.E_409_BOOKMARKS_LIMIT_REACHED  # pragma: no cover

    location_doc = await LocationDocument.get(bookmark.location_id)
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND

    text_doc = await TextDocument.get(location_doc.text_id)
    if not text_doc:
        raise errors.E_404_TEXT_NOT_FOUND  # pragma: no cover

    # construct full label
    location_labels = [location_doc.label]
    parent_location_id = location_doc.parent_id
    while parent_location_id:
        parent_location = await LocationDocument.get(parent_location_id)
        location_labels.insert(0, parent_location.label)
        parent_location_id = parent_location.parent_id

    return await BookmarkDocument(
        user_id=user.id,
        text_id=location_doc.text_id,
        location_id=location_doc.id,
        level=location_doc.level,
        position=location_doc.position,
        label=location_doc.label,
        location_labels=location_labels,
        comment=bookmark.comment,
    ).create()
