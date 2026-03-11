from datetime import UTC, datetime
from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Eq, In, Not, Set
from fastapi import APIRouter, BackgroundTasks, Path, Query, status

from tekst import errors
from tekst.auth import OptionalUserDep, UserDep
from tekst.config import TekstConfig, get_config
from tekst.models.content import ContentArchiveSignature, ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.resources import (
    AnyContentCreate,
    AnyContentDocument,
    AnyContentRead,
    AnyContentUpdate,
    resource_types_mgr,
)
from tekst.search import set_index_ood


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


router = APIRouter(
    prefix="/contents",
    tags=["contents"],
)


@router.post(
    "",
    response_model=AnyContentRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_403_FORBIDDEN,
            errors.E_409_CONTENT_CONFLICT,
            errors.E_400_CONTENT_TYPE_MISMATCH,
        ]
    ),
)
async def create_content(
    content: AnyContentCreate,
    user: UserDep,
) -> AnyContentDocument:
    # check if the resource this content belongs to is writable by user
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content.resource_id,
        await ResourceBaseDocument.query_criteria_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # check for duplicates
    if await ContentBaseDocument.find_one(
        Eq(ContentBaseDocument.resource_id, content.resource_id),
        Eq(ContentBaseDocument.location_id, content.location_id),
        Eq(ContentBaseDocument.archived, False),
        with_children=True,
    ).exists():
        raise errors.E_409_CONTENT_CONFLICT

    # check if resource type matches resource
    if content.resource_type != resource.resource_type:
        raise errors.E_400_CONTENT_TYPE_MISMATCH

    # call the resource's hook for changed contents
    await resource.contents_changed_hook()
    # mark the text's index as out-of-date
    await set_index_ood(resource.text_id, by_public_resource=resource.public)

    # create the content document and return it
    return (
        await resource_types_mgr.get(content.resource_type)
        .content_model()
        .document_model()
        .model_from(content)
        .create()
    )


@router.get(
    "/archive",
    response_model=list[ContentArchiveSignature],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_archived_contents(
    user: OptionalUserDep,
    resource_id: Annotated[PydanticObjectId, Query(alias="resId")],
    location_id: Annotated[PydanticObjectId, Query(alias="locId")],
    limit: Annotated[int, Query(max=102400)] = 10240,
) -> list[ContentArchiveSignature]:
    """
    Returns all content (including archived content)
    for the given resource and location,
    sorted by creation timestamp in descending order.
    """
    # check if passed IDs are valid
    if not await LocationDocument.find_one(LocationDocument.id == location_id).exists():
        raise errors.E_404_LOCATION_NOT_FOUND
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id, with_children=True
    ).exists():
        raise errors.E_404_RESOURCE_NOT_FOUND
    # get archived contents
    return (
        await ContentBaseDocument.find(
            ContentBaseDocument.resource_id == resource_id,
            ContentBaseDocument.location_id == location_id,
            with_children=True,
        )
        .sort(-ContentBaseDocument.created_at)
        .project(ContentArchiveSignature)
        .to_list(limit)
    )


@router.get(
    "/{id}",
    response_model=AnyContentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
        ]
    ),
)
async def get_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> AnyContentDocument:
    """A generic route for retrieving a content by ID from the database"""
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    # check if the resource this content belongs to is readable by user
    resource_read_allowed = content_doc and (
        await ResourceBaseDocument.find_one(
            ResourceBaseDocument.id == content_doc.resource_id,
            await ResourceBaseDocument.query_criteria_read(user),
            with_children=True,
        ).exists()
    )
    if not content_doc or not resource_read_allowed:
        raise errors.E_404_CONTENT_NOT_FOUND
    return content_doc


@router.patch(
    "/{id}",
    response_model=AnyContentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyContentUpdate,
    user: UserDep,
) -> AnyContentDocument:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    # check if the resource this content belongs to is writable by user
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.query_criteria_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # call the resource's hook for changed contents
    await resource.contents_changed_hook()
    # mark the text's index as out-of-date
    await set_index_ood(resource.text_id, by_public_resource=resource.public)

    # archive existing content, obtain an unsaved copy
    content_copy = await content_doc.archive()
    # save updated copy
    return await content_copy.apply_updates(updates, insert=True)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_content(
    user: UserDep,
    background_tasks: BackgroundTasks,
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
    delete_archive: Annotated[bool, Query(alias="deleteArchive")] = False,
) -> None:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.query_criteria_write(user),
        with_children=True,
    )
    if not resource or not (user.is_superuser or user.id not in resource.owner_ids):
        raise errors.E_403_FORBIDDEN

    if not content_doc.archived:
        # call the resource's hook for changed contents
        background_tasks.add_task(resource.contents_changed_hook)
        # mark the text's index as out-of-date
        background_tasks.add_task(
            set_index_ood,
            text_id=resource.text_id,
            by_public_resource=resource.public,
        )

    # delete archived contents
    if delete_archive:
        await ContentBaseDocument.find(
            Eq(ContentBaseDocument.resource_id, content_doc.resource_id),
            Eq(ContentBaseDocument.location_id, content_doc.location_id),
            Eq(ContentBaseDocument.archived, True),
            with_children=True,
        ).delete()

    # delete content
    await content_doc.delete()


@router.post(
    "/{id}/archive",
    status_code=status.HTTP_200_OK,
    response_model=AnyContentRead,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def archive_content(
    user: UserDep,
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyContentDocument:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.query_criteria_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # call the resource's hook for changed contents
    await resource.contents_changed_hook()
    # mark the text's index as out-of-date
    await set_index_ood(resource.text_id, by_public_resource=resource.public)
    # all fine, archive the content
    await content_doc.archive()
    return content_doc


@router.post(
    "/{id}/restore",
    response_model=AnyContentRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_400_INVALID_REQUEST_DATA,
        ]
    ),
)
async def restore_archived_content(
    content_id: Annotated[
        PydanticObjectId,
        Path(
            alias="id",
        ),
    ],
    user: UserDep,
) -> AnyContentDocument:
    """
    Restores the archived content with the given ID, archives any content currently
    present for the same resource/location.
    """
    archived_content_doc: ContentBaseDocument = await ContentBaseDocument.get(
        content_id,
        with_children=True,
    )
    # check if the resource this content belongs to is writable by user
    resource_read_allowed = archived_content_doc and (
        await ResourceBaseDocument.find_one(
            ResourceBaseDocument.id == archived_content_doc.resource_id,
            await ResourceBaseDocument.query_criteria_read(user),
            with_children=True,
        ).exists()
    )
    if not resource_read_allowed:
        raise errors.E_404_CONTENT_NOT_FOUND
    # check if content is archived
    if not archived_content_doc.archived:
        raise errors.update_values(
            errors.E_400_INVALID_REQUEST_DATA,
            {
                "detail": f"Content {content_id} is not archived, "
                "so it cannot be restored from archive."
            },
        )
    # archive any current content for the same resource/location
    await ContentBaseDocument.find(
        Eq(ContentBaseDocument.resource_id, archived_content_doc.resource_id),
        Eq(ContentBaseDocument.location_id, archived_content_doc.location_id),
        Eq(ContentBaseDocument.archived, False),
        with_children=True,
    ).update(Set({ContentBaseDocument.archived: True}))

    # restore formerly archived content as current content
    return await archived_content_doc.model_copy(
        update={
            "id": None,
            "created_at": datetime.now(UTC),
            "archived": False,
        }
    ).save()


@router.get(
    "",
    response_model=list[AnyContentRead],
    status_code=status.HTTP_200_OK,
)
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
    archived: Annotated[
        bool | None,
        Query(description="Include archived content"),
    ] = False,
    limit: Annotated[int, Query(description="Return at most <limit> items")] = 4096,
) -> list[AnyContentDocument]:
    """
    Returns a list of all resource contents matching the given criteria.

    Respects restricted resources and inactive texts.
    As the resulting list may contain contents of different types, the
    returned content objects cannot be typed to their precise resource content type.
    """

    # preprocess resource_ids to add IDs of original resources in case we have patches
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
        await ResourceBaseDocument.query_criteria_read(user),
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
            ({} if archived is None else Eq(ContentBaseDocument.archived, archived)),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )
