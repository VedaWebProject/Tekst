from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.layer_types import (
    AnyUnitCreateBody,
    AnyUnitDocument,
    AnyUnitRead,
    AnyUnitReadBody,
    AnyUnitUpdateBody,
    layer_types_mgr,
)
from tekst.models.layer import LayerBaseDocument
from tekst.models.unit import UnitBaseDocument


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
    responses={status.HTTP_201_CREATED: {"description": "Created"}},
)
async def create_unit(unit: AnyUnitCreateBody, user: UserDep) -> AnyUnitDocument:
    # check if the layer this unit belongs to is writable by user
    if not await LayerBaseDocument.find(
        LayerBaseDocument.id == unit.layer_id,
        LayerBaseDocument.allowed_to_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No write access for units belonging to this layer",
        )
    # check for duplicates
    if await UnitBaseDocument.find_one(
        UnitBaseDocument.layer_id == unit.layer_id,
        UnitBaseDocument.node_id == unit.node_id,
        with_children=True,
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The properties of this unit conflict with another unit",
        )

    return (
        await layer_types_mgr.get(unit.layer_type)
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
    # check if the layer this unit belongs to is readable by user
    layer_read_allowed = unit_doc and (
        await LayerBaseDocument.find_one(
            LayerBaseDocument.id == unit_doc.layer_id,
            await LayerBaseDocument.allowed_to_read(user),
            with_children=True,
        ).exists()
    )
    if not unit_doc or not layer_read_allowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find unit with ID {unit_id}",
        )
    return unit_doc


@router.patch("/{id}", response_model=AnyUnitReadBody, status_code=status.HTTP_200_OK)
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
    # check if unit's layer ID matches updates' layer ID (if it has one specified)
    if updates.layer_id and unit_doc.layer_id != updates.layer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referenced layer ID in unit and updates doesn't match",
        )
    # check if the layer this unit belongs to is writable by user
    layer_write_allowed = await LayerBaseDocument.find_one(
        LayerBaseDocument.id == unit_doc.layer_id,
        LayerBaseDocument.allowed_to_write(user),
        with_children=True,
    ).exists()
    if not layer_write_allowed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No write access for units of layer {unit_doc.layer_id}",
        )
    # apply updates
    await unit_doc.apply(updates.model_dump(exclude_unset=True))
    return unit_doc


@router.get("", response_model=list[AnyUnitReadBody], status_code=status.HTTP_200_OK)
async def find_units(
    user: OptionalUserDep,
    layer_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="layerId",
            description="ID (or list of IDs) of layer(s) to return unit data for",
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
    Returns a list of all data layer units matching the given criteria.

    Respects restricted layers and inactive texts.
    As the resulting list may contain units of different types, the
    returned unit objects cannot be typed to their precise layer unit type.
    """

    readable_layers = await LayerBaseDocument.find(
        await LayerBaseDocument.allowed_to_read(user),
        with_children=True,
    ).to_list()

    unit_docs = (
        await UnitBaseDocument.find(
            In(UnitBaseDocument.layer_id, layer_ids) if layer_ids else {},
            In(UnitBaseDocument.node_id, node_ids) if node_ids else {},
            In(UnitBaseDocument.layer_id, [layer.id for layer in readable_layers]),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    return [
        layer_types_mgr.get(unit_doc.layer_type)
        .unit_model()
        .read_model()(**unit_doc.model_dump())
        for unit_doc in unit_docs
    ]
