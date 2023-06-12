from datetime import datetime

from beanie.operators import Or, Set
from fastapi import APIRouter, HTTPException, status
from pydantic import conlist

from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.models.common import PyObjectId
from tekst.models.layer import LayerBaseDocument
from tekst.models.text import (
    NodeDocument,
    StructureLevelTranslation,
    TextCreate,
    TextDocument,
    TextRead,
    TextUpdate,
)


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(ou: OptionalUserDep, limit: int = 100) -> list[TextRead]:
    restrictions = {"isActive": True} if not (ou and ou.is_superuser) else {}
    return await TextDocument.find(restrictions).limit(limit).to_list()


@router.post("", response_model=TextRead, status_code=status.HTTP_201_CREATED)
async def create_text(su: SuperuserDep, text: TextCreate) -> TextRead:
    if await TextDocument.find_one(
        Or({"title": text.title}, {"slug": text.slug})
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An equal text already exists (same title or slug)",
        )
    return await TextDocument(**text.dict()).create()


# @router.post(
#     "/import",
#     response_model=TextRead,
#     status_code=status.HTTP_201_CREATED,
#     include_in_schema=_cfg.dev_mode,
# )
# async def import_text(
#     file: UploadFile,
#     cfg: TekstConfig = Depends(get_cfg),
# ) -> TextRead:  # pragma: no cover
#     if not cfg.dev_mode:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Endpoint not available in production system",
#         )

#     log.debug(f'Importing text data from uploaded file "{file.filename}" ...')

#     try:
#         text = await importer.import_text(json.loads(await file.read()))
#     except HTTPException as e:
#         log.error(e.detail)
#         raise e
#     except Exception as e:
#         log.error(e)
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid import data: {str(e)}",
#         )
#     finally:
#         await file.close()

#     return text


@router.post(
    "/{id}/insert-level", response_model=TextRead, status_code=status.HTTP_200_OK
)
async def insert_level(
    su: SuperuserDep,
    id: PyObjectId,
    index: int,
    level: conlist(StructureLevelTranslation, min_items=1),
) -> TextRead:
    text: TextDocument = await TextDocument.get(id)

    # text exists?
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {id}",
        )

    # index valid?
    if index < 0 or index > len(text.levels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid level index {index}: " f"Text has {len(text.levels)} levels."
            ),
        )

    # update text itself
    text.levels.insert(index, level)
    if text.default_level >= index:
        text.default_level += 1
    text.modified_at = datetime.utcnow()
    await text.save()

    # update all existing layers with level >= index
    await LayerBaseDocument.find(
        LayerBaseDocument.text_id == id,
        LayerBaseDocument.level >= index,
        with_children=True,
    ).inc({LayerBaseDocument.level: 1})

    # update all existing nodes with level >= index
    await NodeDocument.find(
        NodeDocument.text_id == id, NodeDocument.level >= index
    ).inc({NodeDocument.level: 1})

    # create dummy node on new level
    parent_node = await NodeDocument.find_one(
        NodeDocument.text_id == id,
        NodeDocument.level == index - 1,
        NodeDocument.position == 0,
    )
    only_node = NodeDocument(
        text_id=id,
        parent_id=parent_node.id if parent_node else None,
        level=index,
        position=0,
        label="???",
    )
    await only_node.create()

    # make all nodes of lower level (higher level value) children of this node
    if index < len(text.levels) - 1:
        await NodeDocument.find(
            NodeDocument.text_id == id, NodeDocument.level == index + 1
        ).update(Set({NodeDocument.parent_id: only_node.id}))

    return await TextDocument.get(id)


@router.get("/{id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text(id: PyObjectId) -> TextRead:
    text = await TextDocument.get(id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {id}",
        )
    return text


@router.patch("/{id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def update_text(su: SuperuserDep, id: PyObjectId, updates: TextUpdate) -> dict:
    text = await TextDocument.get(id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text {id} doesn't exist",
        )
    # if updates.slug and updates.slug != text.slug:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Text slug cannot be changed",
    #     )
    await text.apply(updates.dict(exclude_unset=True))
    return await TextDocument.get(id)
