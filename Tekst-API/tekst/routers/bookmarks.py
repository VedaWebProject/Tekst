from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    user: UserDep,
    bookmark_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    bookmark_doc = await BookmarkDocument.get(bookmark_id)
    if not bookmark_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookmark with ID {bookmark_id}",
        )
    if user.id != bookmark_doc.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this bookmark",
        )
    await bookmark_doc.delete()


@router.get("", response_model=list[BookmarkRead], status_code=status.HTTP_200_OK)
async def get_user_bookmarks(user: UserDep) -> list[BookmarkDocument]:
    """Returns all bookmarks that belong to the requesting user"""
    return await BookmarkDocument.find(BookmarkDocument.user_id == user.id).to_list()


@router.post("", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
async def create_bookmark(user: UserDep, bookmark: BookmarkCreate) -> BookmarkDocument:
    """Creates a bookmark for the requesting user"""
    user_bookmarks = await BookmarkDocument.find(
        BookmarkDocument.user_id == user.id
    ).to_list()
    if len(user_bookmarks) >= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User cannot have more than 100 bookmarks",
        )
    if bookmark.location_id in [bm.location_id for bm in user_bookmarks]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A bookmark for this location already exists",
        )

    location_doc = await LocationDocument.get(bookmark.location_id)
    if not location_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {bookmark.location_id} not found",
        )

    text_doc = await TextDocument.get(location_doc.text_id)
    if not text_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Text with ID {location_doc.text_id} not found",
        )

    return await BookmarkDocument(
        user_id=user.id,
        text_id=location_doc.text_id,
        location_id=location_doc.id,
        level=location_doc.level,
        position=location_doc.position,
        label=location_doc.label,
        comment=bookmark.comment,
    ).create()
