from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.layer_types import layer_types_mgr
from tekst.models.layer import LayerBaseDocument
from tekst.models.unit import UnitBase, UnitBaseDocument


def _generate_read_endpoint(
    unit_document_model: type[UnitBase],
    unit_read_model: type[UnitBase],
):
    async def get_unit(id: PydanticObjectId, user: OptionalUserDep) -> unit_read_model:
        """A generic route for reading a unit from the database"""
        unit_doc = await unit_document_model.get(id)
        # check if the layer this unit belongs to is readable by user
        layer_read_allowed = unit_doc and (
            await LayerBaseDocument.find(
                LayerBaseDocument.id == unit_doc.layer_id,
                await LayerBaseDocument.allowed_to_read(user),
                with_children=True,
            ).exists()
        )
        unit_doc = unit_doc if layer_read_allowed else None
        if not unit_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find unit with ID {id}",
            )
        return unit_doc

    return get_unit


def _generate_create_endpoint(
    unit_document_model: type[UnitBase],
    unit_create_model: type[UnitBase],
    unit_read_model: type[UnitBase],
):
    async def create_unit(unit: unit_create_model, user: UserDep) -> unit_read_model:
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
        if await unit_document_model.find(
            UnitDocumentModel.layer_id == unit.layer_id,
            UnitDocumentModel.node_id == unit.node_id,
        ).exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The properties of this unit conflict with another unit",
            )
        return await unit_document_model.model_from(unit).create()

    return create_unit


def _generate_update_endpoint(
    unit_document_model: type[UnitBase],
    unit_read_model: type[UnitBase],
    unit_update_model: type[UnitBase],
):
    async def update_unit(
        id: PydanticObjectId, updates: unit_update_model, user: UserDep
    ) -> unit_read_model:
        unit_doc = await unit_document_model.get(id)
        if not unit_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit {id} doesn't exist",
            )
        # check if unit's layer ID matches updates' layer ID (if it has one specified)
        if updates.layer_id and unit_doc.layer_id != updates.layer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referenced layer ID in unit and updates doesn't match",
            )
        # check if the layer this unit belongs to is writable by user
        layer_write_allowed = (
            await LayerBaseDocument.find(
                LayerBaseDocument.id == unit_doc.layer_id, with_children=True
            )
            .find(LayerBaseDocument.allowed_to_write(user))
            .exists()
        )
        if not layer_write_allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No write access for units of layer {unit_doc.layer_id}",
            )
        # apply updates
        await unit_doc.apply(updates.model_dump(exclude_unset=True))
        return unit_doc

    return update_unit


# initialize unit router
router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# dynamically add all needed routes for every layer type's units
for lt_name, lt_class in layer_types_mgr.get_all().items():
    # type alias unit models
    UnitModel = lt_class.get_unit_model()
    UnitDocumentModel = UnitModel.document_model()
    UnitCreateModel = UnitModel.create_model()
    UnitReadModel = UnitModel.read_model()
    UnitUpdateModel = UnitModel.update_model()
    # add route for reading a unit from the database
    router.add_api_route(
        path=f"/{lt_name}/{{id}}",
        name=f"get_{lt_name}_unit",
        description=f"Returns the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_read_endpoint(
            unit_document_model=UnitDocumentModel,
            unit_read_model=UnitReadModel,
        ),
        methods=["GET"],
        response_model=UnitReadModel,
        status_code=status.HTTP_200_OK,
    )
    # add route for creating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"create_{lt_name}_unit",
        description=f"Creates a {lt_class.get_name()} data layer unit",
        endpoint=_generate_create_endpoint(
            unit_document_model=UnitDocumentModel,
            unit_create_model=UnitCreateModel,
            unit_read_model=UnitReadModel,
        ),
        methods=["POST"],
        response_model=UnitReadModel,
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a unit
    router.add_api_route(
        path=f"/{lt_name}/{{id}}",
        name=f"update_{lt_name}_unit",
        description=f"Updates the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_update_endpoint(
            unit_document_model=UnitDocumentModel,
            unit_read_model=UnitReadModel,
            unit_update_model=UnitUpdateModel,
        ),
        methods=["PATCH"],
        response_model=UnitReadModel,
        status_code=status.HTTP_200_OK,
    )


@router.get("/", response_model=list[dict], status_code=status.HTTP_200_OK)
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
) -> list[dict]:
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

    return [unit_doc.model_dump(camelize_keys=True) for unit_doc in unit_docs]
