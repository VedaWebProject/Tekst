from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Eq, In, Not
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.models.content import ContentBaseDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.resources import (
    AnyContentCreateBody,
    AnyContentDocument,
    AnyContentReadBody,
    AnyContentUpdateBody,
    resource_types_mgr,
)
from tekst.utils.html import sanitize_user_model_html


# initialize content router
router = APIRouter(
    prefix="/contents",
    tags=["contents"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=AnyContentReadBody,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_409_CONFLICT: {"description": "Conflict"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)
async def create_content(
    content: AnyContentCreateBody, user: UserDep
) -> AnyContentDocument:
    # check if the resource this content belongs to is writable by user
    if not await ResourceBaseDocument.find(
        ResourceBaseDocument.id == content.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No write access for contents belonging to this resource",
        )
    # check for duplicates
    if await ContentBaseDocument.find_one(
        ContentBaseDocument.resource_id == content.resource_id,
        ContentBaseDocument.location_id == content.location_id,
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The properties of this content conflict with another content",
        )

    # if the content has a "html" field, sanitize it
    content = sanitize_user_model_html(content)

    return (
        await resource_types_mgr.get(content.resource_type)
        .content_model()
        .document_model()
        .model_from(content)
        .create()
    )


@router.get("/{id}", response_model=AnyContentReadBody, status_code=status.HTTP_200_OK)
async def get_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> AnyContentDocument:
    """A generic route for retrieving a content by ID from the database"""
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    # check if the resource this content belongs to is readable by user
    resource_read_allowed = content_doc and (
        await ResourceBaseDocument.find_one(
            ResourceBaseDocument.id == content_doc.resource_id,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        ).exists()
    )
    if not content_doc or not resource_read_allowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find content with ID {content_id}",
        )
    return content_doc


@router.patch(
    "/{id}",
    response_model=AnyContentReadBody,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)
async def update_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyContentUpdateBody,
    user: UserDep,
) -> AnyContentDocument:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content {content_id} doesn't exist",
        )
    # check if content's resource ID matches updates' resource ID (if any)
    if updates.resource_id and content_doc.resource_id != updates.resource_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referenced resource ID in content and updates doesn't match",
        )
    # check if content's resource type matches updates' resource type
    if updates.resource_type != content_doc.resource_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource type doesn't match existing content's resource type",
        )
    # check if the resource this content belongs to is writable by user
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No write access for resource {content_doc.resource_id}",
        )

    # if the updated content has a "html" field, sanitize it
    updates = sanitize_user_model_html(updates)

    return await content_doc.apply_updates(
        updates, exclude={"id", "resource_id", "location_id", "resource_type"}
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    user: UserDep, content_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No content with ID {content_id}"
        )
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"Cannot delete contents of resource {content_doc.resource_id}",
        )
    # all fine, delete content
    await content_doc.delete()


@router.get("", response_model=list[AnyContentReadBody], status_code=status.HTTP_200_OK)
async def find_contents(
    user: OptionalUserDep,
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="res",
            description="ID (or list of IDs) of resource(s) to return content data for",
        ),
    ] = [],
    location_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="location",
            description="ID (or list of IDs) of location(s) to return content data for",
        ),
    ] = [],
    limit: Annotated[int, Query(description="Return at most <limit> items")] = 4096,
) -> list[AnyContentDocument]:
    """
    Returns a list of all resource contents matching the given criteria.

    Respects restricted resources and inactive texts.
    As the resulting list may contain contents of different types, the
    returned content objects cannot be typed to their precise resource content type.
    """

    # preprocess resource_ids to add IDs of original resources in case we have versions
    if resource_ids:
        resource_ids.append(
            [
                res.original_id
                for res in await ResourceBaseDocument.find(
                    In(ResourceBaseDocument.id, resource_ids),
                    Not(Eq(ResourceBaseDocument.original_id, None)),
                    with_children=True,
                ).to_list()
            ]
        )

    # get readable resources as a subset of the requested ones (might be all resources)
    readable_resources = await ResourceBaseDocument.find(
        In(ResourceBaseDocument.id, resource_ids) if resource_ids else {},
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()

    # get contents matching the given criteria
    return (
        await ContentBaseDocument.find(
            In(ContentBaseDocument.resource_id, resource_ids) if resource_ids else {},
            In(ContentBaseDocument.location_id, location_ids) if location_ids else {},
            In(
                ContentBaseDocument.resource_id,
                [resource.id for resource in readable_resources],
            ),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )
