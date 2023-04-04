from beanie.operators import In
from fastapi import APIRouter, Depends, HTTPException, Query, status

from textrig.auth import UserRead, dep_user, dep_user_optional
from textrig.layer_types import get_layer_types
from textrig.models.common import PyObjectId
from textrig.models.layer import LayerBaseDocument, LayerIdView
from textrig.models.unit import UnitBase, UnitBaseDocument, UnitBaseUpdate


def _generate_read_endpoint(
    unit_document_model: type[UnitBase],
    unit_read_model: type[UnitBase],
):
    async def get_unit(
        id: PyObjectId, user: UserRead | None = Depends(dep_user_optional)
    ) -> unit_read_model:
        """A generic route for reading a unit from the database"""
        unit_doc = await unit_document_model.get(id)
        # check if the layer this unit belongs to is readable by user
        layer_read_allowed = unit_doc and (
            await LayerBaseDocument.find(
                LayerBaseDocument.id == unit_doc.layer_id, with_children=True
            )
            .find(LayerBaseDocument.allowed_to_read(user))
            .exists()
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
    async def create_unit(
        unit: unit_create_model, user: UserRead = Depends(dep_user)
    ) -> unit_read_model:
        # check if the layer this unit belongs to is writable by user
        layer_write_allowed = (
            await LayerBaseDocument.find(
                LayerBaseDocument.id == unit.layer_id, with_children=True
            )
            .find(LayerBaseDocument.allowed_to_write(user))
            .exists()
        )
        if not layer_write_allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No write access for units belonging to this layer",
            )
        dupes_criteria = {"layerId": True, "nodeId": True}
        if await unit_document_model.find(
            unit.dict(include=dupes_criteria)
        ).first_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The properties of this unit conflict with another unit",
            )
        return await unit_document_model(**unit.dict()).create()

    return create_unit


def _generate_update_endpoint(
    unit_document_model: type[UnitBase],
    unit_read_model: type[UnitBase],
    unit_update_model: type[UnitBase],
):
    async def update_unit(
        id: PyObjectId, updates: unit_update_model, user: UserRead = Depends(dep_user)
    ) -> unit_read_model:
        unit_doc = await unit_document_model.get(id)
        if not unit_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit with ID {id} doesn't exist",
            )
        # check if unit's layer ID matches updates' layer ID (if it has one specified)
        if updates.layer_id and unit_doc.layer_id != updates.layer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referenced layer IDs in unit and updates doesn't match",
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
                detail="No write access for units belonging to this layer",
            )
        # apply updates
        await unit_doc.set(updates.dict(exclude_unset=True))
        return unit_doc

    return update_unit


# initialize unit router
router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# dynamically add all needed routes for every layer type's units
for lt_name, lt_class in get_layer_types().items():
    # type alias unit models
    UnitModel = lt_class.get_unit_model()
    UnitDocumentModel = UnitModel.get_document_model(UnitBaseDocument)
    UnitCreateModel = UnitModel.get_create_model()
    UnitReadModel = UnitModel.get_read_model()
    UnitUpdateModel = UnitModel.get_update_model(UnitBaseUpdate)
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
    layer_id: list[PyObjectId] = Query(
        [],
        description="ID (or list of IDs) of layer(s) to return unit data for",
    ),
    node_id: list[PyObjectId] = Query(
        [],
        description="ID (or list of IDs) of node(s) to return unit data for",
    ),
    limit: int = 1000,
    user: UserRead | None = Depends(dep_user_optional),
) -> list[dict]:
    """
    Returns a list of all data layer units matching the given criteria.

    As the resulting list may contain units of different types, the
    returned unit objects cannot be typed to their precise layer unit type.
    """

    readable_layers = (
        await LayerBaseDocument.find(
            LayerBaseDocument.allowed_to_read(user), with_children=True
        )
        .project(LayerIdView)
        .to_list()
    )
    readable_layer_ids = [layer.id for layer in readable_layers]

    units = (
        await UnitBaseDocument.find(
            In(UnitBaseDocument.layer_id, layer_id) if layer_id else {},
            In(UnitBaseDocument.node_id, node_id) if node_id else {},
            In(UnitBaseDocument.layer_id, readable_layer_ids),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    # calling dict(rename_id=True) on these models here makes sure they have
    # "id" instead of "_id", because we're not using a proper read model here
    # that could take care of that automatically (as we don't know the exact type)
    return [unit.dict(rename_id=True) for unit in units]
