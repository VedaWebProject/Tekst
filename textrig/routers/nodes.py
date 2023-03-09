from fastapi import APIRouter, HTTPException, status

from textrig.logging import log
from textrig.models.common import PyObjectId
from textrig.models.text import (
    NodeCreate,
    NodeDocument,
    NodeRead,
    NodeUpdate,
    TextDocument,
)


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.post("", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(node: NodeCreate) -> NodeRead:
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
    return await NodeDocument.from_(node).create()


@router.patch("/{id}", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def update_node(id: PyObjectId, updates: NodeUpdate) -> NodeDocument:
    node_doc = await NodeDocument.get(id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node with ID {id} doesn't exist",
        )
    await node_doc.set(updates.dict(exclude_unset=True))
    return node_doc


@router.get("/{id}", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def get_node(id: PyObjectId) -> NodeDocument:
    node_doc = await NodeDocument.get(id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {id} not found",
        )
    return node_doc


@router.get("", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def find_nodes(
    text_id: PyObjectId,
    level: int = None,
    position: int = None,
    parent_id: PyObjectId = None,
    limit: int = 1000,
) -> list[NodeRead]:
    if level is None and parent_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Request must contain either 'level' or 'parentId'",
        )

    example = dict(textId=text_id)

    if level is not None:
        example["level"] = level

    if position is not None:
        example["position"] = position

    if parent_id:
        example["parentId"] = parent_id

    return await NodeDocument.find(example).limit(limit).to_list()


@router.get(
    "/{id}/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK
)
async def get_children(
    id: PyObjectId,
    limit: int = 1000,
) -> list:
    return await NodeDocument.find(NodeDocument.parent_id == id).limit(limit).to_list()


@router.get("/{id}/next", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def get_next(
    id: PyObjectId,
) -> dict:
    node = await NodeDocument.get(id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node ID {id}",
        )
    node = await NodeDocument.find_one(
        {
            "textId": node.text_id,
            "level": node.level,
            "position": node.position + 1,
        }
    )
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No next node found for node {id}",
        )
    return node
