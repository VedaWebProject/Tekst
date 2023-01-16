from fastapi import APIRouter, HTTPException, status
from textrig.models.text import Node, NodeUpdate, Text
from textrig.logging import log


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.post("", response_model=Node, status_code=status.HTTP_201_CREATED)
async def create_node(node: Node) -> dict:
    if node.id and await Node.get(node.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A node with id {node.id} already exists",
        )

    # find text the node belongs to
    if not await Text.find_one(Text.slug == node.text_slug).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corresponding text '{node.text_slug}' does not exist",
        )
    # check for semantic duplicates
    dupes = await Node.find(
        {"text_slug": node.text_slug, "level": node.level, "index": node.index},
    ).first_or_none()
    if dupes:
        log.warning(f"Cannot create node. Conflict: {node}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing node",
        )
    # all fine
    return await node.create()


@router.get("", response_model=list[Node], status_code=status.HTTP_200_OK)
async def get_nodes(
    text_slug: str,
    level: int = None,
    index: int = None,
    parent_id: str = None,
    limit: int = 1000,
) -> list:
    if level is None and parent_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Request must contain either level or parent_id",
        )

    example = dict(text_slug=text_slug)

    if level is not None:
        example["level"] = level

    if index is not None:
        example["index"] = index

    if parent_id:
        example["parent_id"] = parent_id

    return await Node.find(example).limit(limit).to_list()


@router.patch("", response_model=Node, status_code=status.HTTP_200_OK)
async def update_node(node_update: NodeUpdate) -> dict:
    node: Node = await Node.get(node_update.id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node with ID {node_update.id} doesn't exist",
        )
    await node.set(node_update.dict())
    return node


@router.get(
    "/{node_id}/children", response_model=list[Node], status_code=status.HTTP_200_OK
)
async def get_children(
    node_id: str,
    limit: int = 1000,
) -> list:
    return await Node.find({"parent_id": node_id}).limit(limit).to_list()


@router.get("/{node_id}/next", response_model=Node, status_code=status.HTTP_200_OK)
async def get_next(
    node_id: str,
) -> dict:
    node = await Node.get(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node ID {node_id}",
        )
    node = await Node.find_one(
        {
            "text_slug": node.text_slug,
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
