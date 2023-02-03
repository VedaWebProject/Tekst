from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Path, status
from textrig.layer_types import get_layer_types
from textrig.models.unit import UnitBase, UnitBaseDocument, UnitBaseUpdate


def _generate_read_endpoint(
    UnitDocument: type[UnitBase],
    UnitRead: type[UnitBase],
):
    async def get_unit(
        unit_id: PydanticObjectId = Path(..., alias="unitId")
    ) -> UnitRead:
        """A generic route for reading a unit from the database"""
        unit_doc = await UnitDocument.get(unit_id)
        if not unit_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find unit with ID {unit_id}",
            )
        return unit_doc

    return get_unit


def _generate_create_endpoint(
    UnitDocument: type[UnitBase],
    UnitCreate: type[UnitBase],
    UnitRead: type[UnitBase],
):
    async def create_unit(unit: UnitCreate) -> UnitRead:
        dupes_criteria = {"layerId": True, "nodeId": True}
        if await UnitDocument.find(unit.dict(include=dupes_criteria)).first_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The properties of this unit conflict with another unit",
            )
        return await UnitDocument.from_(unit).create()

    return create_unit


def _generate_update_endpoint(
    UnitDocument: type[UnitBase],
    UnitRead: type[UnitBase],
    UnitUpdate: type[UnitBase],
):
    async def update_unit(updates: UnitUpdate) -> UnitRead:
        unit_doc = await UnitDocument.get(updates.id)
        if not unit_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit with ID {updates.id} doesn't exist",
            )
        await unit_doc.set(updates.dict(exclude={"id"}, exclude_unset=True))
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
        path=f"/{lt_name}/{{unitId}}",
        name=f"get_{lt_name}_unit",
        description=f"Returns the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_read_endpoint(
            UnitDocument=UnitDocumentModel,
            UnitRead=UnitReadModel,
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
            UnitDocument=UnitDocumentModel,
            UnitCreate=UnitCreateModel,
            UnitRead=UnitReadModel,
        ),
        methods=["POST"],
        response_model=UnitReadModel,
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a unit
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"update_{lt_name}_unit",
        description=f"Updates the data for a {lt_class.get_name()} data layer unit",
        endpoint=_generate_update_endpoint(
            UnitDocument=UnitDocumentModel,
            UnitRead=UnitReadModel,
            UnitUpdate=UnitUpdateModel,
        ),
        methods=["PATCH"],
        response_model=UnitReadModel,
        status_code=status.HTTP_200_OK,
    )
