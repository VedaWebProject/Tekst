from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep
from tekst.models.exchange import LocationData
from tekst.models.node import (
    NodeDocument,
    NodeRead,
)
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceCoverage,
    ResourceNodeCoverage,
)
from tekst.models.unit import UnitBaseDocument
from tekst.resource_types import AnyUnitReadBody


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
            alias="res",
            description="ID of resource the requested units belong to",
        ),
    ],
    parent_node_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="parent",
            description="ID of node for which siblings to get associated units for",
        ),
    ] = None,
) -> list[UnitBaseDocument]:
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

    node_ids = [
        node.id
        for node in await NodeDocument.find(
            NodeDocument.text_id == resource.text_id,
            NodeDocument.level == resource.level,
            NodeDocument.parent_id == parent_node_id,
        )
        .sort(+NodeDocument.position)
        .to_list()
    ]

    unit_docs = await UnitBaseDocument.find(
        UnitBaseDocument.resource_id == resource_id,
        In(UnitBaseDocument.node_id, node_ids),
        with_children=True,
    ).to_list()

    unit_docs.sort(key=lambda u: node_ids.index(u.node_id))
    return unit_docs


@router.get(
    "/location-data", response_model=LocationData, status_code=status.HTTP_200_OK
)
async def get_location_data(
    user: OptionalUserDep,
    text_id: Annotated[
        PydanticObjectId,
        Query(alias="txt", description="ID of text to look up data for"),
    ],
    level: Annotated[int, Query(alias="lvl", description="Location level")],
    position: Annotated[int, Query(alias="pos", description="Location position")],
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="res",
            description="ID (or list of IDs) of resource(s) to return unit data for",
        ),
    ] = [],
    only_head_units: Annotated[
        bool,
        Query(
            alias="head",
            description="Only return units referencing the head node of the node path",
        ),
    ] = False,
    limit: Annotated[int, Query(description="Return at most <limit> units")] = 4096,
) -> LocationData:
    """
    Returns the node path from the node with the given level/position
    as the last element, up to its most distant ancestor node
    on structure level 0 as the first element of an array as well as all units
    for the given resource(s) referencing the nodes in the node path.
    """
    node_doc = await NodeDocument.find_one(
        NodeDocument.text_id == text_id,
        NodeDocument.level == level,
        NodeDocument.position == position,
    )
    if not node_doc:
        return LocationData()
    # construct path up to root node
    node_path = [node_doc]
    parent_id = node_doc.parent_id
    while parent_id:
        parent_doc = await NodeDocument.get(parent_id)
        node_path.insert(0, parent_doc)
        parent_id = parent_doc.parent_id
    node_ids = (
        [node.id for node in node_path] if not only_head_units else [node_path[-1].id]
    )

    # collect units
    readable_resources = await ResourceBaseDocument.find(
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()
    unit_docs = (
        await UnitBaseDocument.find(
            In(UnitBaseDocument.resource_id, resource_ids) if resource_ids else {},
            In(UnitBaseDocument.node_id, node_ids) if node_ids else {},
            In(
                UnitBaseDocument.resource_id,
                [resource.id for resource in readable_resources],
            ),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    # return combined data as LocationData
    return LocationData(node_path=node_path, units=unit_docs)


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


@router.get(
    "/resources/{id}/coverage",
    status_code=status.HTTP_200_OK,
    response_model=ResourceCoverage,
)
async def get_resource_coverage_data(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> dict:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    return {
        "covered": await UnitBaseDocument.find(
            UnitBaseDocument.resource_id == resource_id,
            with_children=True,
        ).count(),
        "total": await NodeDocument.find(
            NodeDocument.text_id == resource_doc.text_id,
            NodeDocument.level == resource_doc.level,
        ).count(),
    }


@router.get(
    "/resources/{id}/coverage-details",
    status_code=status.HTTP_200_OK,
    response_model=list[list[ResourceNodeCoverage]],
)
async def get_detailed_resource_coverage_data(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> list[list[dict]]:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    data = (
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
                        "parent_id": 1,
                        "covered": {"$gt": [{"$size": "$units"}, 0]},
                    }
                },
            ],
        )
        .to_list()
    )

    # group nodes by parent
    out = []
    prev_parent_id = "init"
    for node in data:
        if node["parent_id"] == prev_parent_id:
            out[-1].append(node)
        else:
            out.append([node])
        prev_parent_id = node["parent_id"]

    return out
