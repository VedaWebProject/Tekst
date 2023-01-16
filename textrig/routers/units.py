from fastapi import APIRouter, HTTPException, status
from textrig.db import is_unique
from textrig.layer_types import UnitBase, UnitUpdateBase, get_layer_types


def _generate_read_endpoint(unit_read_model: type[UnitBase]):
    async def get_unit(unit_id: str) -> unit_read_model:
        """A generic route for reading a unit from the database"""
        unit = await unit_read_model.get(unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find unit with ID {unit_id}",
            )
        return unit

    return get_unit


def _generate_create_endpoint(
    unit_model: type[UnitBase],
):
    async def create_unit(unit: unit_model) -> unit_model:
        if not await is_unique(unit, ("layer_id", "node_id")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The properties of this unit conflict with another unit",
            )
        return await unit.create()

    return create_unit


def _generate_update_endpoint(
    unit_update_model: type[UnitUpdateBase],
    unit_model: type[UnitBase],
):
    async def update_unit(unit_update: unit_update_model) -> unit_model:
        unit: unit_model = await unit_model.get(unit_update.id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit with ID {unit_update.id} doesn't exist",
            )
        await unit.set(unit_update.dict())
        return unit

    return update_unit


# initialize unit router
router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# dynamically add all needed routes for every layer type's units
for lt_name, lt_class in get_layer_types().items():
    # add route for reading a unit from the database
    router.add_api_route(
        path=f"/{lt_name}/{{unit_id}}",
        name=f"get_{lt_name}_unit",
        description=f"Returns the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_read_endpoint(lt_class.get_unit_model()),
        methods=["GET"],
        response_model=lt_class.get_unit_model(),
        status_code=status.HTTP_200_OK,
    )
    # add route for creating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"create_{lt_name}_unit",
        description=f"Creates a {lt_class.get_name()} data layer unit",
        endpoint=_generate_create_endpoint(
            lt_class.get_unit_model(),
        ),
        methods=["POST"],
        response_model=lt_class.get_unit_model(),
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"update_{lt_name}_unit",
        description=f"Updates the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_update_endpoint(
            lt_class.get_unit_update_model(),
            lt_class.get_unit_model(),
        ),
        methods=["PATCH"],
        response_model=lt_class.get_unit_model(),
        status_code=status.HTTP_200_OK,
    )
