from fastapi import APIRouter, Depends, status
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.layer_types import UnitBase, UnitReadBase, UnitUpdateBase, get_layer_types


def _generate_read_endpoint(unit_read_model: type[UnitReadBase]):
    async def get_unit(
        unit_id: str, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        """A generic route for reading a unit from the database"""
        return await unit_read_model.read(unit_id, db_io)

    return get_unit


def _generate_create_endpoint(
    unit_model: type[UnitBase],
    unit_read_model: type[UnitReadBase],
):
    async def create_unit(
        unit: unit_model, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        return await unit.create(db_io)

    return create_unit


def _generate_update_endpoint(
    unit_update_model: type[UnitUpdateBase],
    unit_read_model: type[UnitReadBase],
):
    async def update_unit(
        unit_update: unit_update_model, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        return await unit_update.update(db_io)

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
        endpoint=_generate_read_endpoint(lt_class.get_unit_read_model()),
        methods=["GET"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_200_OK,
    )
    # add route for creating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"create_{lt_name}_unit",
        description=f"Creates a {lt_class.get_name()} data layer unit",
        endpoint=_generate_create_endpoint(
            lt_class.get_unit_model(),
            lt_class.get_unit_read_model(),
        ),
        methods=["POST"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"update_{lt_name}_unit",
        description=f"Updates the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_update_endpoint(
            lt_class.get_unit_update_model(),
            lt_class.get_unit_read_model(),
        ),
        methods=["PATCH"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_200_OK,
    )
