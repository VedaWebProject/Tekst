from fastapi import APIRouter, Depends, HTTPException, status
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.models.text import Node, NodeRead, NodeUpdate


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.post("", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(node: Node, db_io: DbIO = Depends(get_db_io)) -> dict:
    return await node.create(db_io)


@router.get("", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def get_nodes(
    text_slug: str,
    level: int = None,
    index: int = None,
    parent_id: str = None,
    limit: int = 1000,
    db_io: DbIO = Depends(get_db_io),
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

    return await db_io.find("nodes", example=example, limit=limit)


@router.patch("", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def update_node(
    node_update: NodeUpdate, db_io: DbIO = Depends(get_db_io)
) -> dict:
    return await node_update.update(db_io)


@router.get(
    "/{node_id}/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK
)
async def get_children(
    node_id: str,
    limit: int = 1000,
    db_io: DbIO = Depends(get_db_io),
) -> list:
    return await db_io.find(
        "nodes",
        example={"parent_id": node_id},
        limit=limit,
    )


@router.get("/{node_id}/next", response_model=NodeRead, status_code=status.HTTP_200_OK)
async def get_next(
    node_id: str,
    db_io: DbIO = Depends(get_db_io),
) -> dict:
    node = await db_io.find_one("nodes", node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node ID {node_id}",
        )
    node = NodeRead(**node)
    node = await db_io.find_one_by_example(
        "nodes",
        example={
            "text_slug": node.text_slug,
            "level": node.level,
            "index": node.index + 1,
        },
    )
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No next node found for node {node_id}",
        )
    return node
