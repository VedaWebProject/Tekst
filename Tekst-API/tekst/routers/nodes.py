from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import SuperuserDep
from tekst.logging import log
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
    # find text the node belongs to
    if not await TextDocument.find_one(TextDocument.id == node.text_id).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corresponding text '{node.text_id}' does not exist",
        )
    # check for semantic duplicates
    if await NodeDocument.find_one(
        NodeDocument.text_id == node.text_id,
        NodeDocument.level == node.level,
        NodeDocument.position == node.position,
    ).exists():
        log.warning(f"Cannot create node. Conflict: {node}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing node",
        )
    # all fine
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
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node {node_id} doesn't exist",
        )
    # delete node and everything associated with it
    to_delete = [node_doc]
    units_deleted = 0
    nodes_deleted = 0
    while to_delete:
        curr_node = to_delete[0]
        # delete associated units
        units_deleted += (
            await UnitBaseDocument.find(
                UnitBaseDocument.node_id == curr_node.id, with_children=True
            ).delete()
        ).deleted_count
        # collect child nodes to delete
        to_delete += (
            await NodeDocument.find(NodeDocument.parent_id == curr_node.id)
            .sort(-NodeDocument.position)
            .to_list()
        )
        # decrement position value of all following sibling nodes on this level
        await NodeDocument.find(
            NodeDocument.text_id == curr_node.text_id,
            NodeDocument.level == curr_node.level,
            NodeDocument.position > curr_node.position,
        ).inc({NodeDocument.position: -1})
        # delete current node
        await curr_node.delete()
        nodes_deleted += 1
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
