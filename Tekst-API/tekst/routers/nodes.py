from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, In
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import SuperuserDep
from tekst.models.text import (
    DeleteNodeResult,
    MoveNodeRequestBody,
    NodeCreate,
    NodeDocument,
    NodeRead,
    NodeUpdate,
    TextDocument,
)
from tekst.models.unit import UnitBaseDocument


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.post("", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(su: SuperuserDep, node: NodeCreate) -> NodeRead:
    """
    Creates a new node. The position will be automatically set to the last position
    of the node's parent (or the first parent before that has children).
    """
    # find text the node belongs to
    text = await TextDocument.find_one(TextDocument.id == node.text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corresponding text '{node.text_id}' does not exist",
        )
    # check if level is valid
    if not node.level < len(text.levels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid level {node.level}",
        )
    # determine node position:
    # check if there is a parent
    if node.parent_id is None:
        # no parent, so make it last node on level 0
        # text_id is important in case parent_id == None
        last_sibling = (
            await NodeDocument.find(
                NodeDocument.text_id == text.id,
                NodeDocument.parent_id == node.parent_id,
            )
            .sort(-NodeDocument.position)
            .first_or_none()
        )
        if last_sibling:
            node.position = last_sibling.position + 1
        else:
            node.position = 0
    else:
        # there is a parent, so we need to get the last child of the parent (if any)
        # or the one of the previous parent (and so on...) and use its position + 1
        parent = await NodeDocument.get(node.parent_id)
        while True:
            # text_id is important in case parent_id == None
            last_child = (
                await NodeDocument.find(
                    NodeDocument.text_id == text.id,
                    NodeDocument.parent_id == parent.id,
                )
                .sort(-NodeDocument.position)
                .first_or_none()
            )
            if last_child:
                # found a last child of a parent on next higher level
                node.position = last_child.position + 1
                break
            else:
                # the parent doesn't have any children, so check the previous one
                prev_parent = await NodeDocument.find_one(
                    NodeDocument.text_id == text.id,
                    NodeDocument.level == node.level - 1,
                    NodeDocument.position == parent.position - 1,
                )
                if not prev_parent:
                    # the previous parent doesn't exist, so position will be 0
                    node.position = 0
                    break
                else:
                    # previous parent exists, so remember it for the next iteration
                    parent = prev_parent
    # increment position of all subsequent nodes on this level
    # (including nodes with other parents)
    await NodeDocument.find(
        NodeDocument.text_id == node.text_id,
        NodeDocument.level == node.level,
        NodeDocument.position >= node.position,
    ).inc({NodeDocument.position: 1})
    # all fine, create node
    return await NodeDocument.model_from(node).create()


@router.get("", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def find_nodes(
    text_id: Annotated[PydanticObjectId, Query(alias="textId")],
    level: int = None,
    position: int = None,
    parent_id: Annotated[PydanticObjectId, Query(alias="parentId")] = None,
    limit: int = 1000,
) -> list[NodeDocument]:
    if level is None and parent_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Request must contain either 'level' or 'parentId'",
        )

    example = {"text_id": text_id}

    if level is not None:
        example["level"] = level

    if position is not None:
        example["position"] = position

    if parent_id:
        example["parent_id"] = parent_id

    return await NodeDocument.find(example).limit(limit).to_list()


@router.get("/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def get_children(
    su: SuperuserDep,
    parent_id: Annotated[PydanticObjectId | None, Query(alias="parentId")] = None,
    text_id: Annotated[PydanticObjectId | None, Query(alias="textId")] = None,
    limit: int = 9999,
) -> list:
    if parent_id is None and text_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Request must contain either 'parentId' or 'textId'",
        )
    return (
        await NodeDocument.find(
            And(NodeDocument.text_id == text_id, NodeDocument.parent_id == parent_id)
            if text_id
            else (NodeDocument.parent_id == parent_id),
        )
        .limit(limit)
        .sort(+NodeDocument.position)
        .to_list()
    )


@router.get("/{id}", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def get_node(
    node_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> NodeDocument:
    node_doc = await NodeDocument.get(node_id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_id} not found",
        )
    return node_doc


@router.patch("/{id}", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def update_node(
    su: SuperuserDep,
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: NodeUpdate,
) -> NodeDocument:
    node_doc = await NodeDocument.get(node_id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node {node_id} doesn't exist",
        )
    await node_doc.apply(updates.model_dump(exclude_unset=True))
    return node_doc


@router.delete(
    "/{id}",
    response_model=DeleteNodeResult,
    status_code=status.HTTP_200_OK,
    description=(
        "Deletes the specified node. Also deletes any associated units, "
        "child nodes and units associated with child nodes."
    ),
)
async def delete_node(
    su: SuperuserDep,
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> DeleteNodeResult:
    node_doc = await NodeDocument.get(node_id)
    text_id = node_doc.text_id
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node {node_id} doesn't exist",
        )
    # delete node and everything associated with it
    to_delete = [[node_doc]]
    units_deleted = 0
    nodes_deleted = 0
    while to_delete:
        target_nodes = to_delete[0]
        if len(target_nodes) == 0:
            to_delete.pop(0)
            continue
        target_level = target_nodes[0].level
        target_ids = [n.id for n in target_nodes]
        # delete associated units
        units_deleted += (
            await UnitBaseDocument.find(
                In(UnitBaseDocument.node_id, target_ids), with_children=True
            ).delete()
        ).deleted_count
        # collect child nodes to delete
        to_delete.append(
            await NodeDocument.find(
                In(NodeDocument.parent_id, target_ids),
            )
            .sort(-NodeDocument.position)
            .to_list()
        )
        # decrement position value of all following sibling nodes on this level
        await NodeDocument.find(
            NodeDocument.text_id == text_id,
            NodeDocument.level == target_level,
            NodeDocument.position > target_nodes[0].position,
        ).inc({NodeDocument.position: len(target_nodes) * -1})
        # delete current target nodes
        nodes_deleted += (
            await NodeDocument.find(In(NodeDocument.id, target_ids)).delete()
        ).deleted_count
        to_delete.pop(0)
    return DeleteNodeResult(units=units_deleted, nodes=nodes_deleted)


@router.post(
    "/{id}/move",
    response_model=NodeRead,
    status_code=status.HTTP_200_OK,
    description="Moves the specified node to a new position on its structure level.",
)
async def move_node(
    su: SuperuserDep,
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
    target: MoveNodeRequestBody,
) -> NodeRead:
    node_doc = await NodeDocument.get(node_id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node {node_id} doesn't exist",
        )
    # decrement position of all following nodes
    await NodeDocument.find(
        NodeDocument.text_id == node_doc.text_id,
        NodeDocument.level == node_doc.level,
        NodeDocument.position > node_doc.position,
        NodeDocument.id != node_doc.id,
    ).inc({NodeDocument.position: -1})
    # move node
    node_doc.position = target.position + (
        1 if target.after and target.position < node_doc.position else 0
    )
    node_doc.parent_id = target.parent_id
    await node_doc.save()
    # increment position of all following nodes
    await NodeDocument.find(
        NodeDocument.text_id == node_doc.text_id,
        NodeDocument.level == node_doc.level,
        NodeDocument.position >= node_doc.position,
        NodeDocument.id != node_doc.id,
    ).inc({NodeDocument.position: 1})
    # update nodes positions on all subsequent levels, if any
    await update_node_positions_from_level(node_doc.level + 1, node_doc.text_id)
    # return originally moved node
    return node_doc


async def update_node_positions_from_level(
    level: int, text: PydanticObjectId | TextDocument
) -> None:
    """
    Updates the positions of all nodes on the given level (>0)
    and all subsequent levels. This assumes that the positions of the nodes on
    the parent level of the given level are already correct!
    """
    # as we use the parents' positions to determine the position of the children,
    # this only works for levels >= 1
    if level < 1:
        raise AttributeError("Level must be >= 1")
    # check if text exists
    if not isinstance(text, TextDocument):
        if isinstance(text, PydanticObjectId):
            text = await TextDocument.get(text)
        else:
            raise AttributeError("Text must be a TextDocument or PydanticObjectId")
        if not text:
            raise AttributeError("This text doesn't exist")
    # check if level exists - stop here if it doesn't
    if level >= len(text.levels):
        return
    # update the position of this level's nodes by using the parents' positions
    pos = 0
    async for parent in NodeDocument.find(
        NodeDocument.text_id == text.id,
        NodeDocument.level == level - 1,
    ).sort(+NodeDocument.position):
        # update this parent's children's positions
        async for child in NodeDocument.find(
            NodeDocument.parent_id == parent.id,
        ).sort(+NodeDocument.position):
            child.position = pos
            pos += 1
            await child.save()
    # if there are levels below this level (higher level index), update them as well
    if level + 1 < len(text.levels):
        await update_node_positions_from_level(level + 1, text)
