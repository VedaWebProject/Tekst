from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep
from tekst.models.layer import LayerBaseDocument, LayerNodeCoverage
from tekst.models.text import (
    NodeDocument,
    NodeRead,
)
from tekst.models.unit import UnitBaseDocument


# initialize unit router
router = APIRouter(
    prefix="/browse",
    tags=["browse"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/unit-siblings", response_model=list[dict], status_code=status.HTTP_200_OK)
async def get_unit_siblings(
    user: OptionalUserDep,
    layer_id: Annotated[
        PydanticObjectId,
        Query(description="ID of layer the requested units belong to", alias="layerId"),
    ],
    parent_node_id: Annotated[
        PydanticObjectId | None,
        Query(
            description="ID of node for which siblings to get associated units for",
            alias="parentNodeId",
        ),
    ] = None,
) -> list[dict]:
    """
    Returns a list of all data layer units belonging to the data layer
    with the given ID, associated to nodes that are children of the parent node
    with the given ID.

    As the resulting list may contain units of arbitrary type, the
    returned unit objects cannot be typed to their precise layer unit type.
    Also, the returned unit objects have an additional property containing their
    respective node's label, level and position.
    """

    layer = await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        await LayerBaseDocument.allowed_to_read(user),
        with_children=True,
    )

    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Layer with ID {layer_id} could not be found.",
        )

    nodes = await NodeDocument.find(
        NodeDocument.text_id == layer.text_id,
        NodeDocument.level == layer.level,
        NodeDocument.parent_id == parent_node_id,
    ).to_list()

    unit_docs = await UnitBaseDocument.find(
        UnitBaseDocument.layer_id == layer_id,
        In(UnitBaseDocument.node_id, [node.id for node in nodes]),
        with_children=True,
    ).to_list()

    return [unit_doc.model_dump(camelize_keys=True) for unit_doc in unit_docs]


@router.get(
    "/nodes/path", response_model=list[NodeRead], status_code=status.HTTP_200_OK
)
async def get_node_path(
    text_id: Annotated[PydanticObjectId, Query(alias="textId")],
    level: int,
    position: int,
) -> list[NodeDocument]:
    """
    Returns the text node path from the node with the given level/position
    as the last element, up to its most distant ancestor node
    on structure level 0 as the first element of an array.
    """
    node_doc = await NodeDocument.find_one(
        NodeDocument.text_id == text_id,
        NodeDocument.level == level,
        NodeDocument.position == position,
    )
    if not node_doc:
        return []
    # construct path up to root node
    path = [node_doc]
    parent_id = node_doc.parent_id
    while parent_id:
        parent_doc = await NodeDocument.get(parent_id)
        if parent_doc:
            path.insert(0, parent_doc)
            parent_id = parent_doc.parent_id
        else:
            parent_id = None

    return path


@router.get(
    "/nodes/{id}/path/options-by-head",
    response_model=list[list[NodeRead]],
    status_code=status.HTTP_200_OK,
)
async def get_path_options_by_head_id(
    node_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> list[list[NodeDocument]]:
    """
    Returns the options for selecting text locations derived from the node path of
    the node with the given ID as head.
    """
    node_doc = await NodeDocument.get(node_id)
    if not node_doc:
        return []
    # construct options for this path up to root node
    options = []
    while node_doc and node_doc.parent_id:
        siblings = (
            await NodeDocument.find(NodeDocument.parent_id == node_doc.parent_id)
            .sort(+NodeDocument.position)
            .to_list()
        )
        options.insert(0, siblings)
        node_doc = await NodeDocument.get(node_doc.parent_id)
    # lastly, insert options for root level
    if node_doc:
        root_lvl_options = (
            await NodeDocument.find(
                NodeDocument.text_id == node_doc.text_id,
                NodeDocument.level == 0,
            )
            .sort(+NodeDocument.position)
            .to_list()
        )
        options.insert(0, root_lvl_options)
    return options


@router.get(
    "/nodes/{id}/path/options-by-root",
    response_model=list[list[NodeRead]],
    status_code=status.HTTP_200_OK,
)
async def get_path_options_by_root_id(
    node_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> list[list[NodeDocument]]:
    """
    Returns the options for selecting text locations derived from the node path of
    the node with the given ID as root. At each level, the first option is taken
    as the basis for the next level.
    """
    node_doc = await NodeDocument.get(node_id)
    if not node_doc:
        return []
    # construct options for this path up to max_level
    options = []
    while node_doc:
        children = await NodeDocument.find(
            NodeDocument.parent_id == node_doc.id
        ).to_list()
        if len(children) == 0:
            break
        options.append(children)
        node_doc = children[0]
    return options


@router.get("/layers/{id}/coverage", status_code=status.HTTP_200_OK)
async def get_layer_coverage_data(
    layer_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> list[LayerNodeCoverage]:
    layer_doc = await LayerBaseDocument.find_one(
        LayerBaseDocument.id == layer_id,
        await LayerBaseDocument.allowed_to_read(user),
        with_children=True,
    )
    if not layer_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    return (
        await NodeDocument.find(
            NodeDocument.text_id == layer_doc.text_id,
            NodeDocument.level == layer_doc.level,
        )
        .sort(+NodeDocument.position)
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "units",
                        "localField": "_id",
                        "foreignField": "node_id",
                        "as": "units",
                    }
                },
                {
                    "$project": {
                        "label": 1,
                        "position": 1,
                        "covered": {"$gt": [{"$size": "$units"}, 0]},
                    }
                },
            ],
            projection_model=LayerNodeCoverage,
        )
        .to_list()
    )
