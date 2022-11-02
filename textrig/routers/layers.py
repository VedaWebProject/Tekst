from fastapi import APIRouter, Depends, HTTPException, status
from textrig.config import TextRigConfig, get_config
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.logging import log
from textrig.models.layer import Layer, LayerRead, get_unit_type


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/layers",
    tags=["layers"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


@router.post("", response_model=LayerRead, status_code=status.HTTP_201_CREATED)
async def create_layer(layer: Layer, db_io: DbIO = Depends(get_db_io)) -> LayerRead:

    if not await db_io.find_one("texts", layer.text_slug, "slug"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Corresponding text doesn't exist"
        )

    layer = await db_io.insert_one("layers", layer)
    log.debug(f"Created layer: {layer}")
    return layer


@router.get("/template", status_code=status.HTTP_200_OK)
async def get_layer_template(layer_id: str, db_io: DbIO = Depends(get_db_io)) -> dict:

    layer_data = await db_io.find_one("layers", layer_id)

    if not layer_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Layer doesn't exist")

    # decode layer data: Usually, this is handled automatically by our models, but
    # in this case we're returning a raw dict/JSON, so we have to manually make sure
    # that a) the ID field is called "id" and b) the ObjectId value is encoded as str.
    layer_data = LayerRead(**layer_data).dict()
    layer_data["id"] = str(layer_data["id"])

    # get IDs of all nodes on this structure level as a base for unit templates
    nodes = await db_io.find(
        "nodes",
        example={"textSlug": layer_data["textSlug"], "level": layer_data["level"]},
        projection={"_id", "label"},
        limit=0,
    )

    # import unit type for the requested layer
    UnitType = get_unit_type(layer_data["layerType"])

    # apply generated unit templates to data
    layer_data["units"] = [
        dict(nodeId=str(node["_id"]), **UnitType.get_template()) for node in nodes
    ]

    return layer_data


@router.get("/types", status_code=status.HTTP_200_OK)
async def get_layer_types() -> list:

    pass
