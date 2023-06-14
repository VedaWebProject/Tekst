from datetime import datetime

from beanie.operators import Or, Set
from fastapi import APIRouter, HTTPException, status

from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.models.common import PyObjectId
from tekst.models.layer import LayerBaseDocument
from tekst.models.text import (
    InsertLevelRequest,
    NodeDocument,
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
async def insert_level(su: SuperuserDep, data: InsertLevelRequest) -> TextRead:
    text_doc: TextDocument = await TextDocument.get(data.text_id)

    # text exists?
    if not text_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {data.text_id}",
        )

    # index valid?
    if data.index < 0 or data.index > len(text_doc.levels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid level index {data.index}: "
                f"Text has {len(text_doc.levels)} levels."
            ),
        )

    # update text itself
    text_doc.levels.insert(data.index, data.translations)
    if text_doc.default_level >= data.index:
        text_doc.default_level += 1
    text_doc.modified_at = datetime.utcnow()
    await text_doc.save()

    # update all existing layers with level >= index
    await LayerBaseDocument.find(
        LayerBaseDocument.text_id == data.text_id,
        LayerBaseDocument.level >= data.index,
        with_children=True,
    ).inc({LayerBaseDocument.level: 1})

    # update all existing nodes with level >= index
    await NodeDocument.find(
        NodeDocument.text_id == data.text_id, NodeDocument.level >= data.index
    ).inc({NodeDocument.level: 1})

    # create one dummy node per node on parent level and configure
    # parent-child-relationships on next lower/higher level
    # (different operation if level == 0, as in this case there is no parent level)
    label_prefix = next(
        (
            lvl_trans
            for lvl_trans in data.translations
            if lvl_trans.get("locale", None) == "enUS"
        ),
        data.translations[0],
    ).get("label", "???")
    if data.index == 0:
        dummy_node = NodeDocument(
            text_id=data.text_id,
            parent_id=None,
            level=data.index,
            position=0,
            label=f"{label_prefix} 1",
        )
        await dummy_node.create()
        # make dummy node parent of all nodes on level "index+1" (if exists)
        await NodeDocument.find(
            NodeDocument.text_id == data.text_id, NodeDocument.level == data.index + 1
        ).update(Set({NodeDocument.parent_id: dummy_node.id}))
    else:
        parent_level_nodes = (
            await NodeDocument.find(
                NodeDocument.text_id == data.text_id,
                NodeDocument.level == data.index - 1,
            )
            .sort(+NodeDocument.position)
            .to_list()
        )
        # index > 0, so there is a parent level
        for i, parent_level_node in enumerate(parent_level_nodes):
            # parent of each dummy node is respective node on parent level
            dummy_node = NodeDocument(**parent_level_node.dict(exclude={"id"}))
            dummy_node.parent_id = parent_level_node.id
            dummy_node.level = data.index
            dummy_node.position = i
            dummy_node.label = f"{label_prefix} {i + 1}"
            await dummy_node.create()
            # make dummy node parent of respective nodes on level "index+1" (if exists)
            # that were previously children of dummy's parent node on level "index-1"
            await NodeDocument.find(
                NodeDocument.text_id == data.text_id,
                NodeDocument.level == data.index + 1,
                NodeDocument.parent_id == parent_level_node.id,
            ).update(Set({NodeDocument.parent_id: dummy_node.id}))

    return text_doc


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
