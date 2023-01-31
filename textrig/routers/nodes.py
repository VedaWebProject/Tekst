from fastapi import APIRouter, HTTPException, status, Path
from textrig.logging import log
from textrig.models.text import (
    NodeCreate,
    NodeDocument,
    NodeRead,
    NodeUpdate,
    TextDocument,
)
from textrig.utils.validators import validate_id
from beanie import PydanticObjectId


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
        NodeDocument.index == node.index
    ).exists():
        log.warning(f"Cannot create node. Conflict: {node}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing node",
        )
    # all fine
    return await NodeDocument.from_(node).create()


@router.get("", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def get_nodes(
    text_id: PydanticObjectId,
    level: int = None,
    index: int = None,
    parent_id: PydanticObjectId = None,
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

    if index is not None:
        example["index"] = index

    if parent_id:
        example["parentId"] = parent_id

    return await NodeDocument.find(example).limit(limit).to_list()


@router.patch("", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def update_node(updates: NodeUpdate) -> dict:
    node_doc = await NodeDocument.get(updates.id)
    if not node_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node with ID {updates.id} doesn't exist",
        )
    await node_doc.set(updates.dict(exclude={"id"}, exclude_unset=True))
    return node_doc


@router.get(
    "/{nodeId}/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK
)
async def get_children(
    node_id: PydanticObjectId = Path(..., alias="nodeId"),
    limit: int = 1000,
) -> list:
    return await NodeDocument.find({"parentId": node_id}).limit(limit).to_list()


@router.get("/{nodeId}/next", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def get_next(
    node_id: PydanticObjectId = Path(..., alias="nodeId"),
) -> dict:
    validate_id(node_id)
    node = await NodeDocument.get(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node ID {node_id}",
        )
    node = await NodeDocument.find_one(
        {
            "textId": node.text_id,
            "level": node.level,
            "index": node.index + 1,
        }
    )
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No next node found for node {node_id}",
        )
    return node
