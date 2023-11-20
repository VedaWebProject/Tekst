from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.layer_types import layer_type_manager
from tekst.models.layer import AnyLayerRead, LayerBase, LayerBaseDocument
from tekst.models.text import TextDocument


def _generate_read_endpoint(
    layer_document_model: type[LayerBase], layer_read_model: type[LayerBase]
):
    async def get_layer(
        id: PydanticObjectId, user: OptionalUserDep
    ) -> layer_read_model:
        """A generic route for reading a layer definition from the database"""
        layer_doc = await layer_document_model.find(
            layer_document_model.id == id, layer_document_model.allowed_to_read(user)
        ).first_or_none()
        if not layer_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find layer with ID {id}",
            )
        # return only fields that are not restricted for this user
        return layer_doc.model_dump(
            exclude=layer_doc.restricted_fields(user and user.id)
        )

    return get_layer


def _generate_create_endpoint(
    layer_document_model: type[LayerBase],
    layer_create_model: type[LayerBase],
    layer_read_model: type[LayerBase],
):
    async def create_layer(
        layer: layer_create_model, user: UserDep
    ) -> layer_read_model:
        if not await TextDocument.get(layer.text_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Layer refers to non-existent text '{layer.text_id}'",
            )
        # force some values on creation
        layer.owner_id = user.id
        layer.proposed = False
        layer.public = False
        return await layer_document_model.model_from(layer).create()

    return create_layer


def _generate_update_endpoint(
    layer_document_model: type[LayerBase],
    layer_read_model: type[LayerBase],
    layer_update_model: type[LayerBase],
):
    async def update_layer(
        id: PydanticObjectId, updates: layer_update_model, user: UserDep
    ) -> layer_read_model:
        layer_doc: layer_document_model = (
            await layer_document_model.find(layer_document_model.id == id)
            .find(layer_document_model.allowed_to_write(user))
            .first_or_none()
        )
        if not layer_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Layer {id} doesn't exist or requires extra permissions",
            )
        await layer_doc.apply(updates.model_dump(exclude_unset=True))
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
for lt_name, lt_class in layer_type_manager.get_all().items():
    # type alias unit models
    LayerModel = lt_class.get_layer_model()
    LayerDocumentModel = LayerModel.get_document_model()
    LayerCreateModel = LayerModel.get_create_model()
    LayerReadModel = LayerModel.get_read_model()
    LayerUpdateModel = LayerModel.get_update_model()
    # add route for reading a layer definition from the database
    router.add_api_route(
        path=f"/{lt_name}/{{id}}",
        name=f"get_{lt_name}_layer",
        description=f"Returns the data for a {lt_class.get_label()} data layer",
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
        description=f"Creates a {lt_class.get_label()} data layer definition",
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
        description=f"Updates the data for a {lt_class.get_label()} data layer",
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


@router.get("", response_model=list[AnyLayerRead], status_code=status.HTTP_200_OK)
async def find_layers(
    user: OptionalUserDep,
    text_id: Annotated[PydanticObjectId, Query(alias="textId")],
    level: int = None,
    layer_type: Annotated[str, Query(alias="layerType")] = None,
    limit: int = 1000,
) -> list[dict]:
    """
    Returns a list of all data layers matching the given criteria.

    As the resulting list of data layers may contain layers of different types, the
    returned layer objects cannot be typed to their precise layer type.
    """

    example = {"text_id": text_id}

    # add to example
    if level is not None:
        example["level"] = level
    if layer_type:
        example["layer_type"] = layer_type

    active_texts = await TextDocument.find(
        TextDocument.is_active == True  # noqa: E712
    ).to_list()

    active_texts_restriction = (
        In(LayerBaseDocument.text_id, [text.id for text in active_texts])
        if not (user and user.is_superuser)
        else {}
    )

    layer_docs = (
        await LayerBaseDocument.find(example, with_children=True)
        .find(
            LayerBaseDocument.allowed_to_read(user),
            active_texts_restriction,
        )
        .limit(limit)
        .to_list()
    )

    uid = user and user.id
    return [
        layer_doc.model_dump(exclude=layer_doc.restricted_fields(uid))
        for layer_doc in layer_docs
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
#
#     layer_type_manager = layer_type_manager

#     # decode layer data: Usually, this is handled automatically by our models, but
#     # in this case we're returning a raw dict/JSON, so we have to manually make sure
#     # that a) the ID field is called "id" and b) the DocumentId is encoded as str.
#     layer_read_model = layer_type_manager \
#       .get(layer_data["layerType"]).get_layer_read_model()
#     layer_data = layer_read_model(**layer_data).model_dump()

#     # import unit type for the requested layer
#     template = layer_type_manager \
#       .get(layer_data["layerType"]).prepare_import_template()
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
#         model_dump(nodeId=str(node["_id"]), **node_template) for node in nodes
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


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=AnyLayerRead)
async def get_generic_layer_data_by_id(
    layer_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> dict:
    layer_doc = (
        await LayerBaseDocument.find(
            LayerBaseDocument.id == layer_id, with_children=True
        )
        .find(LayerBaseDocument.allowed_to_read(user))
        .first_or_none()
    )
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    return layer_doc.model_dump(exclude=layer_doc.restricted_fields(user and user.id))
