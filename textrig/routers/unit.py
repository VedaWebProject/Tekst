from fastapi import APIRouter, Depends, HTTPException, status
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.layer_types import LayerTypePluginABC, get_layer_types
from textrig.logging import log


def _generate_read_endpoint(unit_read_model: type[LayerTypePluginABC.UnitReadBase]):
    async def get_unit(
        unit_id: str, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        """A generic route for reading a unit from the database"""
        unit = await db_io.find_one("units", unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A unit with the given ID cannot be found",
            )
        return unit

    return get_unit


def _generate_create_endpoint(
    unit_model: type[LayerTypePluginABC.UnitBase],
    unit_read_model: type[LayerTypePluginABC.UnitReadBase],
):
    async def create_unit(
        unit: unit_model, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        # check for conflicts
        if await db_io.find_one_by_example(
            "units", {"layer_id": unit.layer_id, "node_id": unit.node_id}
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A text with an equal slug already exists",
            )
        # TODO: check if layer ID and node ID are valid!
        pass
        # insert new unit
        unit = await db_io.insert_one("units", unit)
        log.debug(f"Created unit: {unit}")
        return unit

    return create_unit


def _generate_update_endpoint(
    unit_update_model: type[LayerTypePluginABC.UnitUpdateBase],
    unit_read_model: type[LayerTypePluginABC.UnitReadBase],
):
    async def update_unit(
        unit_id: str, unit_update: unit_update_model, db_io: DbIO = Depends(get_db_io)
    ) -> unit_read_model:
        if not await db_io.update("units", unit_id, unit_update):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not update unit {unit_id}",
            )

        unit_data = await db_io.find_one("units", unit_id)

        if not unit_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not return data for unit {unit_id}",
            )

        return unit_data

    return update_unit


# initialize unit router
router = APIRouter(
    prefix="/unit",
    tags=["unit"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# dynamically add all needed routes for every layer type's units
for lt_name, lt_class in get_layer_types().items():
    # add route for reading a unit from the database
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"Get {lt_class.get_name()} unit",
        description=f"Returns the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_read_endpoint(lt_class.get_unit_read_model()),
        methods=["GET"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_200_OK,
        tags=[lt_name],
    )
    # add route for creating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"Create {lt_class.get_name()} unit",
        description=f"Creates a {lt_class.get_name()} data layer unit",
        endpoint=_generate_create_endpoint(
            lt_class.get_unit_model(), lt_class.get_unit_read_model()
        ),
        methods=["POST"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_201_CREATED,
        tags=[lt_name],
    )
    # add route for updating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"Update {lt_class.get_name()} unit",
        description=f"Updates the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_update_endpoint(
            lt_class.get_unit_update_model(), lt_class.get_unit_read_model()
        ),
        methods=["PATCH"],
        response_model=lt_class.get_unit_read_model(),
        status_code=status.HTTP_200_OK,
        tags=[lt_name],
    )
