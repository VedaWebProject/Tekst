from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep
from tekst.models.node import (
    NodeDocument,
    NodeRead,
)
from tekst.models.resource import ResourceBaseDocument, ResourceNodeCoverage
from tekst.models.unit import UnitBaseDocument
from tekst.resource_types import AnyUnitRead, AnyUnitReadBody, resource_types_mgr


# initialize unit router
router = APIRouter(
    prefix="/browse",
    tags=["browse"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get(
    "/unit-siblings",
    response_model=list[AnyUnitReadBody],
    status_code=status.HTTP_200_OK,
)
async def get_unit_siblings(
    user: OptionalUserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Query(
            description="ID of resource the requested units belong to",
            alias="resourceId",
        ),
    ],
    parent_node_id: Annotated[
        PydanticObjectId | None,
        Query(
            description="ID of node for which siblings to get associated units for",
            alias="parentNodeId",
        ),
    ] = None,
) -> list[AnyUnitRead]:
    """
    Returns a list of all resource units belonging to the resource
    with the given ID, associated to nodes that are children of the parent node
    with the given ID.

    As the resulting list may contain units of arbitrary type, the
    returned unit objects cannot be typed to their precise resource unit type.
    Also, the returned unit objects have an additional property containing their
    respective node's label, level and position.
    """

    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} could not be found.",
        )

    nodes = await NodeDocument.find(
        NodeDocument.text_id == resource.text_id,
        NodeDocument.level == resource.level,
        NodeDocument.parent_id == parent_node_id,
    ).to_list()

    unit_docs = await UnitBaseDocument.find(
        UnitBaseDocument.resource_id == resource_id,
        In(UnitBaseDocument.node_id, [node.id for node in nodes]),
        with_children=True,
    ).to_list()

    return [
        resource_types_mgr.get(unit_doc.resource_type)
        .unit_model()
        .read_model()(**unit_doc.model_dump())
        for unit_doc in unit_docs
    ]


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
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
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
    while node_doc:
        siblings = (
            await NodeDocument.find(
                NodeDocument.text_id == node_doc.text_id,
                NodeDocument.parent_id == node_doc.parent_id,
            )
            .sort(+NodeDocument.position)
            .to_list()
        )
        options.insert(0, siblings)
        node_doc = await NodeDocument.get(node_doc.parent_id)
    return options


@router.get(
    "/nodes/{id}/path/options-by-root",
    response_model=list[list[NodeRead]],
    status_code=status.HTTP_200_OK,
)
async def get_path_options_by_root(
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
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


@router.get("/resources/{id}/coverage", status_code=status.HTTP_200_OK)
async def get_resource_coverage_data(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> list[ResourceNodeCoverage]:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    return (
        await NodeDocument.find(
            NodeDocument.text_id == resource_doc.text_id,
            NodeDocument.level == resource_doc.level,
        )
        .sort(+NodeDocument.position)
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "units",
                        "localField": "_id",
                        "foreignField": "node_id",
                        "let": {"node_id": "$_id", "resource_id": resource_id},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$node_id", "$$node_id"]},
                                            {"$gte": ["$resource_id", "$$resource_id"]},
                                        ]
                                    }
                                }
                            },
                            {"$project": {"_id": 1}},
                        ],
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
            projection_model=ResourceNodeCoverage,
        )
        .to_list()
    )
