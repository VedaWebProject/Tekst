from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Path, Query, status

from tekst.auth import SuperuserDep
from tekst.logging import log
from tekst.models.text import (
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
    return await NodeDocument(**node.model_dump()).create()


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

    example = dict(textId=text_id)

    if level is not None:
        example["level"] = level

    if position is not None:
        example["position"] = position

    if parent_id:
        example["parentId"] = parent_id

    return await NodeDocument.find(example).limit(limit).to_list()


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
            detail=f"Node {node_id} doesn't exist or requires extra permissions",
        )
    await node_doc.apply(updates.model_dump(exclude_unset=True))
    return node_doc


@router.get(
    "/{id}/children", response_model=list[NodeRead], status_code=status.HTTP_200_OK
)
async def get_children(
    node_id: Annotated[PydanticObjectId, Path(alias="id")],
    limit: int = 9999,
) -> list:
    return (
        await NodeDocument.find(NodeDocument.parent_id == node_id)
        .limit(limit)
        .to_list()
    )
