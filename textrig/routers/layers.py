from fastapi import APIRouter, Depends, HTTPException, status

from textrig.auth import UserRead, dep_user, dep_user_optional
from textrig.layer_types import get_layer_types
from textrig.models.common import PyObjectId
from textrig.models.layer import (
    LayerBase,
    LayerBaseDocument,
    LayerBaseUpdate,
)
from textrig.models.text import TextDocument


def _generate_read_endpoint(
    layer_document_model: type[LayerBase], layer_read_model: type[LayerBase]
):
    async def get_layer(
        id: PyObjectId, user: UserRead | None = Depends(dep_user_optional)
    ) -> layer_read_model:
        """A generic route for reading a layer definition from the database"""
        layer_doc = (
            await layer_document_model.find(layer_document_model.id == id)
            .find(layer_document_model.allowed_to_read(user))
            .first_or_none()
        )
        if not layer_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find layer with ID {id}",
            )
        # return only fields that are not restricted for this user
        return layer_doc.dict(exclude=layer_doc.restricted_fields(user and user.id))

    return get_layer


def _generate_create_endpoint(
    layer_document_model: type[LayerBase],
    layer_create_model: type[LayerBase],
    layer_read_model: type[LayerBase],
):
    async def create_layer(
        layer: layer_create_model, user: UserRead = Depends(dep_user)
    ) -> layer_read_model:
        if not await TextDocument.get(layer.text_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Layer refers to non-existent text '{layer.text_id}'",
            )
        uid = user.id if user else "no_id"
        if uid != layer.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Layer's owner ID doesn't match requesting user's ID",
            )
        return await layer_document_model(**layer.dict()).create()

    return create_layer


def _generate_update_endpoint(
    layer_document_model: type[LayerBase],
    layer_read_model: type[LayerBase],
    layer_update_model: type[LayerBase],
):
    async def update_layer(
        id: PyObjectId, updates: layer_update_model, user: UserRead = Depends(dep_user)
    ) -> layer_read_model:
        layer_doc: layer_document_model = (
            await layer_document_model.find(layer_document_model.id == id)
            .find(layer_document_model.allowed_to_write(user))
            .first_or_none()
        )
        if not layer_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Layer with ID {id} doesn't exist",
            )
        await layer_doc.set(updates.dict(exclude_unset=True))
        return layer_doc

    return update_layer


router = APIRouter(
    prefix="/layers",
    tags=["layers"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


# dynamically add all needed routes for every layer type's layer definitions
for lt_name, lt_class in get_layer_types().items():
    # type alias unit models
    LayerModel = lt_class.get_layer_model()
    LayerDocumentModel = LayerModel.get_document_model(LayerBaseDocument)
    LayerCreateModel = LayerModel.get_create_model()
    LayerReadModel = LayerModel.get_read_model()
    LayerUpdateModel = LayerModel.get_update_model(LayerBaseUpdate)
    # add route for reading a layer definition from the database
    router.add_api_route(
        path=f"/{lt_name}/{{id}}",
        name=f"get_{lt_name}_layer",
        description=f"Returns the data for a {lt_class.get_name()} data layer",
        endpoint=_generate_read_endpoint(
            layer_document_model=LayerDocumentModel, layer_read_model=LayerReadModel
        ),
        methods=["GET"],
        response_model=LayerReadModel,
        status_code=status.HTTP_200_OK,
    )
    # add route for creating a layer
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"create_{lt_name}_layer",
        description=f"Creates a {lt_class.get_name()} data layer definition",
        endpoint=_generate_create_endpoint(
            layer_document_model=LayerDocumentModel,
            layer_create_model=LayerCreateModel,
            layer_read_model=LayerReadModel,
        ),
        methods=["POST"],
        response_model=LayerReadModel,
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a layer
    router.add_api_route(
        path=f"/{lt_name}/{{id}}",
        name=f"update_{lt_name}_layer",
        description=f"Updates the data for a {lt_class.get_name()} data layer",
        endpoint=_generate_update_endpoint(
            layer_document_model=LayerDocumentModel,
            layer_read_model=LayerReadModel,
            layer_update_model=LayerUpdateModel,
        ),
        methods=["PATCH"],
        response_model=LayerReadModel,
        status_code=status.HTTP_200_OK,
    )


# ADDITIONAL ROUTE DEFINITIONS...


@router.get("", response_model=list[dict], status_code=status.HTTP_200_OK)
async def find_layers(
    text_id: PyObjectId,
    level: int = None,
    layer_type: str = None,
    limit: int = 1000,
    user: UserRead | None = Depends(dep_user_optional),
) -> list[dict]:
    """
    Returns a list of all data layers matching the given criteria.

    As the resulting list of data layers may contain layers of different types, the
    returned layer objects cannot be typed to their precise layer type.
    """

    example = {"textId": text_id}

    # add to example
    if level is not None:
        example["level"] = level
    if layer_type:
        example["layerType"] = layer_type

    layers = (
        await LayerBaseDocument.find(example, with_children=True)
        .find(LayerBaseDocument.allowed_to_read(user))
        .limit(limit)
        .to_list()
    )

    # calling dict(rename_id=True) on these models makes sure they have
    # "id" instead of "_id", because we're not using a proper read model here
    # that could take care of that automatically (as we don't know the exact type)
    uid = user and user.id
    return [
        layer.dict(rename_id=True, exclude=layer.restricted_fields(uid))
        for layer in layers
    ]


#
#   TODO: rebuild template endpoint using beanie logic
#

# @router.get("/template", status_code=status.HTTP_200_OK)
# async def get_layer_template(layer_id: str, db_io: DbIO = Depends(get_db_io)) -> dict:
#     layer_data = await db_io.find_one("layers", layer_id)

#     if not layer_data:
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST,
#             detail=f"Layer with ID {layer_id} doesn't exist",
#         )

#     # decode layer data: Usually, this is handled automatically by our models, but
#     # in this case we're returning a raw dict/JSON, so we have to manually make sure
#     # that a) the ID field is called "id" and b) the DocumentId is encoded as str.
#     layer_read_model = get_layer_type(layer_data["layerType"]).get_layer_read_model()
#     layer_data = layer_read_model(**layer_data).dict()

#     # import unit type for the requested layer
#     template = get_layer_type(layer_data["layerType"]).prepare_import_template()
#     # apply data from layer instance
#     template["layerId"] = str(layer_data["id"])
#     template["_level"] = layer_data["level"]
#     template["_title"] = layer_data["title"]
#     template["_description"] = layer_data.get("description", None)

#     # generate unit template
#     node_template = {key: None for key in template["_unitSchema"].keys()}

#     # get IDs of all nodes on this structure level as a base for unit templates
#     nodes = await db_io.find(
#         "nodes",
#         example={"textSlug": layer_data["textSlug"], "level": layer_data["level"]},
#         projection={"_id", "label"},
#         limit=0,
#     )

#     # fill in unit templates with IDs
#     template["units"] = [
#         dict(nodeId=str(node["_id"]), **node_template) for node in nodes
#     ]

#     # create temporary file and stream it as a file response
#     tempfile = NamedTemporaryFile(mode="w")
#     tempfile.write(json.dumps(template, indent=2))
#     tempfile.flush()

#     # prepare headers
#     filename = (
#         f"{layer_data['textSlug']}_layer_{safe_name(template['layerId'])}"
#         "_template.json"
#     )
#     headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

#     log.debug(f"Serving layer template as temporary file {tempfile.name}")
#     return FileResponse(
#         tempfile.name,
#         headers=headers,
#         media_type="application/json",
#         background=BackgroundTask(tempfile.close),
#     )


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_generic_layer_data_by_id(
    id: PyObjectId, user: UserRead | None = Depends(dep_user_optional)
) -> dict:
    layer_doc = (
        await LayerBaseDocument.find(LayerBaseDocument.id == id, with_children=True)
        .find(LayerBaseDocument.allowed_to_read(user))
        .first_or_none()
    )
    if not layer_doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {id}")
    return layer_doc.dict(exclude=layer_doc.restricted_fields(user and user.id))
