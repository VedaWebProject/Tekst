from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError
from textrig.db.io import DbIO
from textrig.dependencies import get_db_io
from textrig.logging import log
from textrig.models.common import DocumentId
from textrig.models.text import Node, NodeRead


router = APIRouter(
    prefix="/node",
    tags=["node"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def get_router() -> APIRouter:
    """Normalized access to the router object"""
    return router


# ROUTES DEFINITIONS...


@router.post("", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(node: Node, db_io: DbIO = Depends(get_db_io)) -> dict:
    # find text the node belongs to
    text = await db_io.find_one("texts", node.text_slug, field="slug")

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The corresponding text does not exist",
        )

    try:
        return await db_io.insert_one("nodes", node)
    except DuplicateKeyError:
        log.warning(f"Cannot create node. Conflict: {node}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing node",
        )


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
        example["parent_id"] = DocumentId(parent_id)

    return await db_io.find("nodes", example=example, limit=limit)


@router.get("/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK)
async def get_children(
    text_slug: str,
    node_id: str,
    limit: int = 1000,
    db_io: DbIO = Depends(get_db_io),
) -> list:
    return await db_io.find(
        "nodes",
        example={"text_slug": text_slug, "parent_id": node_id},
        limit=limit,
        hint="textSlug_parentId_level_index",
    )
