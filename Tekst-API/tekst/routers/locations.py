from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, In, NotIn
from fastapi import APIRouter, Path, Query, status

from tekst import errors, tasks
from tekst.auth import SuperuserDep
from tekst.models.content import ContentBaseDocument
from tekst.models.location import (
    DeleteLocationResult,
    LocationCreate,
    LocationDocument,
    LocationRead,
    LocationUpdate,
)
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import (
    MoveLocationRequestBody,
    TextDocument,
)
from tekst.resources import resource_types_mgr


router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


# ROUTES DEFINITIONS...


@router.post(
    "",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_400_INVALID_TEXT,
            errors.E_400_INVALID_LEVEL,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_location(su: SuperuserDep, location: LocationCreate) -> LocationRead:
    """
    Creates a new location. The position will be automatically set to the last position
    of the location's parent (or the first parent before that has children).
    """
    # find text the location belongs to
    text = await TextDocument.find_one(TextDocument.id == location.text_id)
    if not text:
        raise errors.E_400_INVALID_TEXT
    # check if level is valid
    if not location.level < len(text.levels):
        raise errors.E_400_INVALID_LEVEL
    # determine location position:
    # check if there is a parent
    if location.parent_id is None:
        # no parent, so make it last location on level 0
        # text_id is important in case parent_id == None
        last_sibling = (
            await LocationDocument.find(
                LocationDocument.text_id == text.id,
                LocationDocument.parent_id == location.parent_id,
            )
            .sort(-LocationDocument.position)
            .first_or_none()
        )
        if last_sibling:
            location.position = last_sibling.position + 1
        else:
            location.position = 0
    else:
        # there is a parent, so we need to get the last child of the parent (if any)
        # or the one of the previous parent (and so on...) and use its position + 1
        parent = await LocationDocument.get(location.parent_id)
        while True:
            last_child = (
                await LocationDocument.find(
                    LocationDocument.parent_id == parent.id,
                )
                .sort(-LocationDocument.position)
                .first_or_none()
            )
            if last_child:
                # found a last child of a parent on next higher level
                location.position = last_child.position + 1
                break
            else:
                # the parent doesn't have any children, so check the previous one
                prev_parent = await LocationDocument.find_one(
                    LocationDocument.text_id == text.id,
                    LocationDocument.level == location.level - 1,
                    LocationDocument.position == parent.position - 1,
                )
                if not prev_parent:
                    # the previous parent doesn't exist, so position will be 0
                    location.position = 0
                    break
                else:
                    # previous parent exists, so remember it for the next iteration
                    parent = prev_parent
    # increment position of all subsequent locations on this level
    # (including locations with other parents)
    await LocationDocument.find(
        LocationDocument.text_id == location.text_id,
        LocationDocument.level == location.level,
        LocationDocument.position >= location.position,
    ).inc({LocationDocument.position: 1})
    # all fine, create location
    return await LocationDocument.model_from(location).create()


@router.get(
    "",
    response_model=list[LocationRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_400_LOCATION_NO_LEVEL_NOR_PARENT,
        ]
    ),
)
async def find_locations(
    text_id: Annotated[
        PydanticObjectId,
        Query(alias="txt", description="ID of text to find locations for"),
    ],
    level: Annotated[
        int, Query(alias="lvl", description="Structure level to find locations for")
    ] = None,
    position: Annotated[
        int, Query(alias="pos", description="Position value of locations to find")
    ] = None,
    parent_id: Annotated[
        PydanticObjectId,
        Query(alias="parent", description="ID of parent location to find children of"),
    ] = None,
    limit: Annotated[
        int, Query(description="Return at most <limit> locations")
    ] = 16384,
) -> list[LocationDocument]:
    if level is None and parent_id is None:
        raise errors.E_400_LOCATION_NO_LEVEL_NOR_PARENT

    example = {"text_id": text_id}

    if level is not None:
        example["level"] = level

    if position is not None:
        example["position"] = position

    if parent_id:
        example["parent_id"] = parent_id

    return await LocationDocument.find(example).limit(limit).to_list()


@router.get(
    "/children",
    response_model=list[LocationRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_400_LOCATION_CHILDREN_NO_PARENT_NOR_TEXT,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def get_children(
    su: SuperuserDep,
    text_id: Annotated[
        PydanticObjectId | None,
        Query(alias="txt", description="ID of text to find locations for"),
    ] = None,
    parent_id: Annotated[
        PydanticObjectId | None,
        Query(alias="parent", description="ID of parent location to find children of"),
    ] = None,
    limit: int = 8192,
) -> list:
    if parent_id is None and text_id is None:
        raise errors.E_400_LOCATION_CHILDREN_NO_PARENT_NOR_TEXT
    return (
        await LocationDocument.find(
            And(
                (LocationDocument.text_id == text_id) if text_id else {},
                LocationDocument.parent_id == parent_id,
            )
        )
        .limit(limit)
        .sort(+LocationDocument.position)
        .to_list()
    )


@router.get(
    "/{id}",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_LOCATION_NOT_FOUND,
        ]
    ),
)
async def get_location(
    location_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> LocationDocument:
    location_doc = await LocationDocument.get(location_id)
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND
    return location_doc


@router.patch(
    "/{id}",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_LOCATION_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_location(
    su: SuperuserDep,
    location_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: LocationUpdate,
) -> LocationDocument:
    location_doc = await LocationDocument.get(location_id)
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND
    return await location_doc.apply_updates(updates)


@router.delete(
    "/{id}",
    response_model=DeleteLocationResult,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_LOCATION_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_location(
    su: SuperuserDep,
    location_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> DeleteLocationResult:
    """
    Deletes the specified location. Also deletes any associated contents,
    child locations and contents associated with child locations.
    """
    location_doc = await LocationDocument.get(location_id)
    if not location_doc:
        raise errors.E_404_LOCATION_NOT_FOUND
    text_id = location_doc.text_id
    # delete location and everything associated with it
    to_delete = [[location_doc]]
    contents_deleted = 0
    locations_deleted = 0
    while to_delete:
        target_locations = to_delete[0]
        if len(target_locations) == 0:
            to_delete.pop(0)
            continue
        target_level = target_locations[0].level
        target_ids = [n.id for n in target_locations]
        # delete associated contents
        contents_deleted += (
            await ContentBaseDocument.find(
                In(ContentBaseDocument.location_id, target_ids), with_children=True
            ).delete()
        ).deleted_count
        # collect child locations to delete
        to_delete.append(
            await LocationDocument.find(
                In(LocationDocument.parent_id, target_ids),
            )
            .sort(-LocationDocument.position)
            .to_list()
        )
        # decrement position value of all following sibling locations on this level
        await LocationDocument.find(
            LocationDocument.text_id == text_id,
            LocationDocument.level == target_level,
            LocationDocument.position > target_locations[0].position,
        ).inc({LocationDocument.position: len(target_locations) * -1})
        # delete current target locations
        locations_deleted += (
            await LocationDocument.find(In(LocationDocument.id, target_ids)).delete()
        ).deleted_count
        to_delete.pop(0)

    # create background task that calls the
    # content's resource's hook for updated content
    if contents_deleted > 0:
        for resource in await ResourceBaseDocument.find_all(
            with_children=True
        ).to_list():
            await tasks.create_task(
                resource_types_mgr.get(resource.resource_type).contents_changed_hook,
                tasks.TaskType.CONTENTS_CHANGED_HOOK,
                resource.id,
                None,
                resource.id,  # will be passed to contents_changed_hook
            )

    return DeleteLocationResult(contents=contents_deleted, locations=locations_deleted)


@router.post(
    "/{id}/move",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_LOCATION_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def move_location(
    su: SuperuserDep,
    location_id: Annotated[PydanticObjectId, Path(alias="id")],
    target: MoveLocationRequestBody,
) -> LocationRead:
    """Moves the specified location to a new position on its level."""
    # get location document
    location: LocationDocument = await LocationDocument.get(location_id)
    if not location:
        raise errors.E_404_LOCATION_NOT_FOUND
    # define initial working vars
    text_levels = len((await TextDocument.get(location.text_id)).levels)
    forward = target.position > location.position
    direction_mod = 1 if forward else -1
    position = target.position + (1 if target.after else 0) - (1 if forward else 0)
    distance = abs(position - location.position)
    to_move = [location]
    # set new location parent if needed
    if location.parent_id != target.parent_id:
        location.parent_id = target.parent_id
        await location.save()
    # move location and all children
    for level in range(location.level, text_levels):
        # determine sequence of locations that have to be shifted
        shift_start = (
            (to_move[0].position + len(to_move))
            if forward
            else (to_move[0].position - distance)
        )
        shift_end = shift_start + distance - 1
        # log.debug(f"shift: {shift_start}-{shift_end} on level {level}")
        to_shift = (
            await LocationDocument.find(
                LocationDocument.text_id == location.text_id,
                LocationDocument.level == level,
                LocationDocument.position >= shift_start,
                LocationDocument.position <= shift_end,
                NotIn(LocationDocument.id, [n.id for n in to_move]),
            )
            .sort(+LocationDocument.position)
            .to_list()
        )
        # move locations
        await LocationDocument.find(
            In(LocationDocument.id, [n.id for n in to_move])
        ).inc({LocationDocument.position: distance * direction_mod})
        # shift jumped locations
        await LocationDocument.find(
            In(LocationDocument.id, [n.id for n in to_shift])
        ).inc({LocationDocument.position: len(to_move) * direction_mod * -1})
        # prepare next level
        if level < text_levels - 1:
            to_move = (
                await LocationDocument.find(
                    In(LocationDocument.parent_id, [n.id for n in to_move]),
                )
                .sort(+LocationDocument.position)
                .to_list()
            )
            if not to_move:  # pragma: no cover
                break
            distance = await LocationDocument.find(
                In(LocationDocument.parent_id, [n.id for n in to_shift]),
            ).count()
    return await LocationDocument.get(location_id)
