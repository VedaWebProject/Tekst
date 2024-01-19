from typing import Annotated, Literal

from beanie import PydanticObjectId
from beanie.operators import In, NotIn
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import OptionalUserDep, UserDep
from tekst.models.content import ContentBaseDocument
from tekst.models.exchange import LocationData
from tekst.models.node import (
    NodeDocument,
    NodeRead,
)
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceCoverage,
    ResourceCoverageDetails,
)
from tekst.resources import AnyContentReadBody


# initialize content router
router = APIRouter(
    prefix="/browse",
    tags=["browse"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get(
    "/content-siblings",
    response_model=list[AnyContentReadBody],
    status_code=status.HTTP_200_OK,
)
async def get_content_siblings(
    user: OptionalUserDep,
    resource_id: Annotated[
        PydanticObjectId,
        Query(
            alias="res",
            description="ID of resource the requested contents belong to",
        ),
    ],
    parent_node_id: Annotated[
        PydanticObjectId | None,
        Query(
            alias="parent",
            description="ID of node for which siblings to get associated contents for",
        ),
    ] = None,
) -> list[ContentBaseDocument]:
    """
    Returns a list of all resource contents belonging to the resource
    with the given ID, associated to nodes that are children of the parent node
    with the given ID.

    As the resulting list may contain contents of arbitrary type, the
    returned content objects cannot be typed to their precise resource content type.
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

    content_docs = await ContentBaseDocument.find(
        ContentBaseDocument.resource_id == resource_id,
        In(ContentBaseDocument.node_id, node_ids),
        with_children=True,
    ).to_list()

    # if the resource is a version, we also have to find the original's contents
    # that are missing in the requested resource version
    if resource.original_id:
        original_content_docs = await ContentBaseDocument.find(
            ContentBaseDocument.resource_id == resource.original_id,
            In(ContentBaseDocument.node_id, node_ids),
            NotIn(ContentBaseDocument.node_id, [u.node_id for u in content_docs]),
            with_children=True,
        ).to_list()
    else:
        original_content_docs = []

    # combine contents lists, sort by reference node position, return
    content_docs.extend(original_content_docs)
    content_docs.sort(key=lambda u: node_ids.index(u.node_id))
    return content_docs


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
            description="ID (or list of IDs) of resource(s) to return content data for",
        ),
    ] = [],
    only_head_contents: Annotated[
        bool,
        Query(
            alias="head",
            description="Only return contents referencing the head node of the path",
        ),
    ] = False,
    limit: Annotated[int, Query(description="Return at most <limit> contents")] = 4096,
) -> LocationData:
    """
    Returns the node path from the node with the given level/position
    as the last element, up to its most distant ancestor node
    on structure level 0 as the first element of an array as well as all contents
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
        [node.id for node in node_path]
        if not only_head_contents
        else [node_path[-1].id]
    )

    # collect contents
    readable_resources = await ResourceBaseDocument.find(
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()
    content_docs = (
        await ContentBaseDocument.find(
            In(ContentBaseDocument.resource_id, resource_ids) if resource_ids else {},
            In(ContentBaseDocument.node_id, node_ids) if node_ids else {},
            In(
                ContentBaseDocument.resource_id,
                [resource.id for resource in readable_resources],
            ),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )

    # return combined data as LocationData
    return LocationData(node_path=node_path, contents=content_docs)


@router.get("/nearest-content", status_code=status.HTTP_200_OK)
async def get_nearest_content(
    user: OptionalUserDep,
    position: Annotated[int, Query(alias="pos", description="Location position")],
    target_resource_id: Annotated[
        PydanticObjectId,
        Query(
            alias="targetRes",
            description="ID of resource to return nearest location with content for",
        ),
    ] = [],
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="res",
            description="ID (or list of IDs) of resource(s) to return content data for",
        ),
    ] = [],
    mode: Annotated[
        Literal["preceding", "subsequent"],
        Query(
            description=(
                "Whether to look for the nearest preceding "
                "or subsequent location with content"
            )
        ),
    ] = "subsequent",
    limit: Annotated[int, Query(description="Return at most <limit> contents")] = 4096,
) -> int:
    """
    Finds the nearest location the given resource holds content for and returns
    data for that location.
    """
    # we don't check read access here, because are passing data to the location-data
    # endpoint later anyway and it already checks for permissions
    resource_doc = await ResourceBaseDocument.get(
        target_resource_id, with_children=True
    )
    if not resource_doc:  # pragma: no cover
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"No resource with ID {target_resource_id}",
        )

    # get all nodes before/after said location
    nodes = (
        await NodeDocument.find(
            NodeDocument.text_id == resource_doc.text_id,
            NodeDocument.level == resource_doc.level,
            (NodeDocument.position < position)
            if mode == "preceding"
            else (NodeDocument.position > position),
        )
        .sort(
            +NodeDocument.position if mode == "subsequent" else -NodeDocument.position
        )
        .to_list()
    )
    # prepare 404 (we'll reuse it later)
    not_found_exception = HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail=(
            f"No content found {'before' if mode == 'preceding' else 'after'} "
            f"position {position} for resource {target_resource_id}."
        ),
    )
    if not nodes:  # pragma: no cover
        raise not_found_exception

    # get contents for these nodes
    contents = await ContentBaseDocument.find(
        ContentBaseDocument.resource_id == target_resource_id,
        In(ContentBaseDocument.node_id, [node.id for node in nodes]),
        with_children=True,
    ).to_list()
    if not contents:  # pragma: no cover
        raise not_found_exception

    # find out nearest of those locations with contents
    nodes = [
        node for node in nodes if node.id in [content.node_id for content in contents]
    ]

    # return position of nearest node with contents of the target resource
    return nodes[0].position


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
        "covered": await ContentBaseDocument.find(
            ContentBaseDocument.resource_id == resource_id,
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
    response_model=ResourceCoverageDetails,
)
async def get_detailed_resource_coverage_data(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
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
    data: list[dict] = (
        await NodeDocument.find(
            NodeDocument.text_id == resource_doc.text_id,
            NodeDocument.level == resource_doc.level,
        )
        .sort(+NodeDocument.position)
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "contents",
                        "localField": "_id",
                        "foreignField": "node_id",
                        "let": {"node_id": "$_id", "resource_id": resource_id},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$node_id", "$$node_id"]},
                                            {"$eq": ["$resource_id", "$$resource_id"]},
                                        ]
                                    }
                                }
                            },
                            {"$project": {"_id": 1}},
                        ],
                        "as": "contents",
                    }
                },
                {
                    "$project": {
                        "id": "$_id",
                        "label": 1,
                        "position": 1,
                        "parent_id": 1,
                        "covered": {"$gt": [{"$size": "$contents"}, 0]},
                    }
                },
            ],
        )
        .to_list()
    )

    # get parent level node location labels
    parent_node_locations = await NodeDocument.get_node_locations(
        text_id=resource_doc.text_id, for_level=resource_doc.level - 1
    )

    # group nodes by parent
    out = []
    parent_labels = []
    prev_parent_id = "init"
    for node in data:
        if node["parent_id"] == prev_parent_id:
            out[-1].append(node)
        else:
            out.append([node])
            if node["parent_id"]:
                parent_labels.append(parent_node_locations[str(node["parent_id"])])
        prev_parent_id = node["parent_id"]

    return ResourceCoverageDetails(nodes_coverage=out, parent_labels=parent_labels)
