from typing import Annotated, Literal

from beanie import PydanticObjectId
from beanie.operators import In, NotIn
from fastapi import APIRouter, Query, status

from tekst import errors
from tekst.auth import OptionalUserDep
from tekst.models.browse import LocationData
from tekst.models.content import ContentBaseDocument
from tekst.models.location import (
    LocationDocument,
    LocationRead,
)
from tekst.models.resource import (
    ResourceBaseDocument,
)
from tekst.models.text import TextDocument
from tekst.resources import AnyContentRead


router = APIRouter(
    prefix="/browse",
    tags=["browse"],
)


async def _get_content_context(
    resource: ResourceBaseDocument,
    parent_location_id: PydanticObjectId | None,
) -> list[ContentBaseDocument]:
    """
    Returns a list of all resource contents belonging to locations that are children
    of the given parent location, sorted by reference location position.
    """
    # find IDs of all locations that are children of the requested parent
    location_ids = [
        location.id
        for location in await LocationDocument.find(
            LocationDocument.text_id == resource.text_id,
            LocationDocument.level == resource.level,
            LocationDocument.parent_id == parent_location_id,
        )
        .sort(+LocationDocument.position)
        .to_list()
    ]

    # find direct contents of the requested resource for the requested locations
    content_docs = await ContentBaseDocument.find(
        ContentBaseDocument.resource_id == resource.id,
        In(ContentBaseDocument.location_id, location_ids),
        with_children=True,
    ).to_list()

    # if the resource is a version, we also have to find the original's contents
    # that are missing in the requested resource version
    if resource.original_id:
        original_content_docs = await ContentBaseDocument.find(
            ContentBaseDocument.resource_id == resource.original_id,
            In(ContentBaseDocument.location_id, location_ids),
            NotIn(
                ContentBaseDocument.location_id, [u.location_id for u in content_docs]
            ),
            with_children=True,
        ).to_list()
    else:
        original_content_docs = []

    # combine contents lists, sort by reference location position, return
    content_docs.extend(original_content_docs)
    content_docs.sort(key=lambda c: location_ids.index(c.location_id))

    return content_docs


@router.get(
    "/context",
    response_model=list[AnyContentRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_content_context(
    user: OptionalUserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Query(
            alias="res",
            description="ID of resource the requested contents belong to",
        ),
    ],
    parent_location_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="parent",
            description="ID of parent location to get child contents for",
        ),
    ] = None,
) -> list[ContentBaseDocument]:
    """
    Returns a list of all resource contents belonging to the resource
    with the given ID, associated to locations that are children of the parent location
    with the given ID.
    """

    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )

    if not resource:
        raise errors.E_404_RESOURCE_NOT_FOUND

    return await _get_content_context(resource, parent_location_id)


@router.get(
    "",
    response_model=LocationData,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_LOCATION_NOT_FOUND,
        ]
    ),
)
async def get_location_data(
    user: OptionalUserDep,
    location_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="id",
            description="ID of location to request data for",
        ),
    ] = None,
    text_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="txt",
            description=(
                "ID of text the target location belongs to "
                "(needed if no location ID is given)"
            ),
        ),
    ] = None,
    level: Annotated[
        int | None,
        Query(
            alias="lvl",
            description=(
                "Location level (only used if no location ID is given, "
                "text's default level is used by default)"
            ),
        ),
    ] = None,
    position: Annotated[
        int,
        Query(
            alias="pos",
            description="Location position (only used if no location ID is given)",
        ),
    ] = 0,
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="res",
            description=(
                "List of IDs of resources to return contents for "
                "(assumes all if none are given)"
            ),
        ),
    ] = [],
    only_head_contents: Annotated[
        bool,
        Query(
            alias="head",
            description="Only return contents for the head location of the path",
        ),
    ] = False,
) -> LocationData:
    """
    Returns the location path from the location with the given ID or text/level/position
    as the last element, up to its most distant ancestor location
    on structure level 0 as the first element of an array as well as all contents
    for the given resource(s) referencing the locations in the location path.
    """
    # limit for number of contents fetched from DB per request
    # (internal constant to conveniently adjust it later if needed)
    contents_fetch_limit = 512

    # find target location
    location_doc = None
    if location_id:
        location_doc = await LocationDocument.get(location_id)
    elif text_id:
        text_doc = await TextDocument.get(text_id)
        if text_doc:
            lvl = level if level is not None else text_doc.default_level
            location_doc = await LocationDocument.find_one(
                LocationDocument.text_id == text_id,
                LocationDocument.level == lvl,
                LocationDocument.position == position or 0,
            )
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND

    # construct path up to root location
    location_path = [location_doc]
    parent_id = location_doc.parent_id
    while parent_id:
        parent_doc = await LocationDocument.get(parent_id)
        location_path.insert(0, parent_doc)
        parent_id = parent_doc.parent_id
    location_ids = (
        [location.id for location in location_path]
        if not only_head_contents
        else [location_path[-1].id]
    )

    # collect contents for target resources belonging to locations present in
    # the location path (resource.level <= location_doc.level)
    target_resources = await ResourceBaseDocument.find(
        In(ResourceBaseDocument.id, resource_ids) if resource_ids else {},
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()
    content_docs = (
        await ContentBaseDocument.find(
            In(ContentBaseDocument.location_id, location_ids or []),
            In(
                ContentBaseDocument.resource_id,
                [resource.id for resource in target_resources],
            ),
            with_children=True,
        )
        .limit(contents_fetch_limit)
        .to_list()
    )
    # add combined contents (content context) of resources that are on the subordinate
    # level of the target location (if the resources are configured to support this!)
    for res in [
        res
        for res in target_resources
        if res.level == location_doc.level + 1
        and res.config.general.enable_content_context
    ]:
        content_docs.extend(await _get_content_context(res, location_doc.id))

    # find IDs of previous and next location on same level
    prev_loc = (
        await LocationDocument.find_one(
            LocationDocument.text_id == location_doc.text_id,
            LocationDocument.level == location_doc.level,
            LocationDocument.position == location_doc.position - 1,
        )
    ) or (
        await LocationDocument.find(
            LocationDocument.text_id == location_doc.text_id,
            LocationDocument.level == location_doc.level,
        )
        .sort(-LocationDocument.position)
        .first_or_none()
    )
    next_loc = (
        await LocationDocument.find_one(
            LocationDocument.text_id == location_doc.text_id,
            LocationDocument.level == location_doc.level,
            LocationDocument.position == location_doc.position + 1,
        )
    ) or (
        await LocationDocument.find_one(
            LocationDocument.text_id == location_doc.text_id,
            LocationDocument.level == location_doc.level,
            LocationDocument.position == 0,
        )
    )

    # return location path, adjacent locations' IDs
    # and requested contents as combined LocationData
    return LocationData(
        location_path=location_path,
        previous_loc_id=prev_loc.id if prev_loc else None,
        next_loc_id=next_loc.id if next_loc else None,
        contents=content_docs,
    )


@router.get(
    "/nearest-content-location",
    status_code=status.HTTP_200_OK,
    response_model=LocationRead,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_404_NOT_FOUND,
            errors.E_400_INVALID_REQUEST_DATA,
        ]
    ),
)
async def get_nearest_content_location(
    user: OptionalUserDep,
    location_id: Annotated[
        PydanticObjectId,
        Query(
            alias="loc",
            description="ID of the location to start from",
        ),
    ],
    resource_id: Annotated[
        PydanticObjectId,
        Query(
            alias="res",
            description="ID of resource to return nearest location with content for",
        ),
    ],
    direction: Annotated[
        Literal["before", "after"],
        Query(
            alias="dir",
            description=(
                "Whether to look for the nearest preceding (before) "
                "or subsequent (after) location with content"
            ),
        ),
    ] = "after",
) -> LocationDocument:
    """
    Finds the nearest location the given resource holds content for and returns it.
    """
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    location_doc = await LocationDocument.get(location_id)
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND
    if (
        location_doc.level != resource_doc.level
        or location_doc.text_id != resource_doc.text_id
    ):
        raise errors.E_400_INVALID_REQUEST_DATA

    # get all locations before/after said location
    locations = (
        await LocationDocument.find(
            LocationDocument.text_id == resource_doc.text_id,
            LocationDocument.level == resource_doc.level,
            (LocationDocument.position < location_doc.position)
            if direction == "before"
            else (LocationDocument.position > location_doc.position),
        )
        .sort(
            +LocationDocument.position
            if direction == "after"
            else -LocationDocument.position
        )
        .aggregate([{"$project": {"position": 1}}])
        .to_list()
    )
    if not locations:  # pragma: no cover
        raise errors.E_404_NOT_FOUND

    # get contents for these locations
    contents = (
        await ContentBaseDocument.find(
            ContentBaseDocument.resource_id == resource_id,
            In(
                ContentBaseDocument.location_id,
                [location.get("_id") for location in locations],
            ),
            with_children=True,
        )
        .aggregate([{"$project": {"location_id": 1}}])
        .to_list()
    )
    if not contents:  # pragma: no cover
        raise errors.E_404_NOT_FOUND

    # find out nearest of those locations with contents
    locations = [
        location
        for location in locations
        if location.get("_id") in [content.get("location_id") for content in contents]
    ]

    if len(locations) == 0:  # pragma: no cover
        raise errors.E_404_NOT_FOUND

    # return ID of nearest location with contents of the target resource
    return await LocationDocument.get(locations[0].get("_id"))
