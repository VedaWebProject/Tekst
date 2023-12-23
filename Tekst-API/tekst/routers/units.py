from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.models.resource import ResourceBaseDocument
from tekst.models.unit import UnitBaseDocument
from tekst.resource_types import (
    AnyUnitCreateBody,
    AnyUnitDocument,
    AnyUnitRead,
    AnyUnitReadBody,
    AnyUnitUpdateBody,
    resource_types_mgr,
)


# initialize unit router
router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=AnyUnitReadBody,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_409_CONFLICT: {"description": "Conflict"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def create_unit(unit: AnyUnitCreateBody, user: UserDep) -> AnyUnitDocument:
    # check if the resource this unit belongs to is writable by user
    if not await ResourceBaseDocument.find(
        ResourceBaseDocument.id == unit.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No write access for units belonging to this resource",
        )
    # check for duplicates
    if await UnitBaseDocument.find_one(
        UnitBaseDocument.resource_id == unit.resource_id,
        UnitBaseDocument.node_id == unit.node_id,
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The properties of this unit conflict with another unit",
        )

    return (
        await resource_types_mgr.get(unit.resource_type)
        .unit_model()
        .document_model()
        .model_from(unit)
        .create()
    )


@router.get("/{id}", response_model=AnyUnitReadBody, status_code=status.HTTP_200_OK)
async def get_unit(
    unit_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> AnyUnitDocument:
    """A generic route for retrieving a unit by ID from the database"""
    unit_doc = await UnitBaseDocument.get(unit_id, with_children=True)
    # check if the resource this unit belongs to is readable by user
    resource_read_allowed = unit_doc and (
        await ResourceBaseDocument.find_one(
            ResourceBaseDocument.id == unit_doc.resource_id,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        ).exists()
    )
    if not unit_doc or not resource_read_allowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find unit with ID {unit_id}",
        )
    return unit_doc


@router.patch(
    "/{id}",
    response_model=AnyUnitReadBody,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def update_unit(
    unit_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyUnitUpdateBody,
    user: UserDep,
) -> AnyUnitDocument:
    unit_doc = await UnitBaseDocument.get(unit_id, with_children=True)
    if not unit_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unit {unit_id} doesn't exist",
        )
    # check if unit's resource ID matches updates' resource ID (if it has one specified)
    if updates.resource_id and unit_doc.resource_id != updates.resource_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referenced resource ID in unit and updates doesn't match",
        )
    # check if the resource this unit belongs to is writable by user
    resource_write_allowed = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == unit_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists()
    if not resource_write_allowed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No write access for units of resource {unit_doc.resource_id}",
        )
    # apply updates
    await unit_doc.apply(updates.model_dump(exclude_unset=True))
    return unit_doc


@router.get("", response_model=list[AnyUnitReadBody], status_code=status.HTTP_200_OK)
async def find_units(
    user: OptionalUserDep,
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="resourceId",
            description="ID (or list of IDs) of resource(s) to return unit data for",
        ),
    ] = [],
    node_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="nodeId",
            description="ID (or list of IDs) of node(s) to return unit data for",
        ),
    ] = [],
    limit: Annotated[int, Query(description="Return at most <limit> items")] = 1000,
) -> list[AnyUnitRead]:
    """
    Returns a list of all resource units matching the given criteria.

    Respects restricted resources and inactive texts.
    As the resulting list may contain units of different types, the
    returned unit objects cannot be typed to their precise resource unit type.
    """

    readable_resources = await ResourceBaseDocument.find(
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()

    unit_docs = (
        await UnitBaseDocument.find(
            In(UnitBaseDocument.resource_id, resource_ids) if resource_ids else {},
            In(UnitBaseDocument.node_id, node_ids) if node_ids else {},
            In(
                UnitBaseDocument.resource_id,
                [resource.id for resource in readable_resources],
            ),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    return [
        resource_types_mgr.get(unit_doc.resource_type)
        .unit_model()
        .read_model()(**unit_doc.model_dump())
        for unit_doc in unit_docs
    ]
