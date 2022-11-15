import json
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from textrig.config import TextRigConfig, get_config
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.layer_types import get_layer_type, get_layer_types
from textrig.logging import log
from textrig.models.layer import Layer, LayerRead
from textrig.utils.strings import safe_name


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/layer",
    tags=["layer"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


# ROUTES DEFINITIONS...


@router.post("", response_model=LayerRead, status_code=status.HTTP_201_CREATED)
async def create_layer(layer: Layer, db_io: DbIO = Depends(get_db_io)) -> LayerRead:
    if not await db_io.find_one("texts", layer.text_slug, "slug"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Corresponding text doesn't exist"
        )
    # TODO: Check is layer type is valid?
    # ...
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
    # that a) the ID field is called "id" and b) the DocumentId value is encoded as str.
    layer_data = LayerRead(**layer_data).dict()

    # import unit type for the requested layer
    template = get_layer_type(layer_data["layerType"]).prepare_import_template()
    # apply data from layer instance
    template["layerId"] = str(layer_data["id"])
    template["_level"] = layer_data["level"]
    template["_title"] = layer_data["title"]
    template["_description"] = layer_data["description"]

    # generate unit template
    node_template = {key: None for key in template["_unitSchema"].keys()}

    # get IDs of all nodes on this structure level as a base for unit templates
    nodes = await db_io.find(
        "nodes",
        example={"textSlug": layer_data["textSlug"], "level": layer_data["level"]},
        projection={"_id", "label"},
        limit=0,
    )

    # fill in unit templates with IDs
    template["units"] = [
        dict(nodeId=str(node["_id"]), **node_template) for node in nodes
    ]

    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")
    tempfile.write(json.dumps(template, indent=2))
    tempfile.flush()

    # prepare headers
    filename = (
        f"{layer_data['textSlug']}_layer_{safe_name(template['layerId'])}"
        "_template.json"
    )
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    log.debug(f"Serving layer template as temporary file {tempfile.name}")
    return FileResponse(
        tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


@router.get("/types", status_code=status.HTTP_200_OK)
async def map_layer_types() -> dict:
    """Returns a list of all available data layer unit types"""
    resp_data = {}
    for lt_name, lt_type in get_layer_types().items():
        resp_data[lt_name] = {
            "name": lt_type.get_name(),
            "description": lt_type.get_description(),
        }
    return resp_data
