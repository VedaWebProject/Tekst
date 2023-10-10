
from copy import deepcopy
from pathlib import Path as SysPath
from typing import Annotated, List

from beanie import PydanticObjectId
from beanie.operators import Or, Set, Unset
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.dependencies import get_temp_dir
from tekst.models.exchange import NodeDefinition, TextStructureDefinition
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
    restrictions = {} if (ou and ou.is_superuser) else {"is_active": True}
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
    return await TextDocument.model_from(text).create()


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


@router.get("/{id}/template", status_code=status.HTTP_200_OK)
async def download_structure_template(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    temp_dir_name: str = Depends(get_temp_dir),
) -> FileResponse:
    """
    Download the structure template for a text to help compose a structure
    definition that can later be uploaded to the server
    """
    # find text
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )
    # create template for text
    structure_def: TextStructureDefinition = TextStructureDefinition()
    curr_node_def: NodeDefinition | None = None
    dummy_node = NodeDefinition(
        label="Label for the first node on level '{}' (required!)",
    )
    for n in range(len(text.levels)):
        node = deepcopy(dummy_node)
        node.label = node.label.format(text.levels[n][0]["label"])
        if curr_node_def is None:
            structure_def.nodes.append(node)
        else:
            curr_node_def.nodes = []
            curr_node_def.nodes.append(node)
        curr_node_def = node
    # validate template
    try:
        TextStructureDefinition.model_validate(structure_def)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating template",
        )
    # allocate and write temporary file
    temp_file_name = f"{text.slug}_structure_template.json"
    temp_file_path = SysPath(temp_dir_name) / temp_file_name
    with open(temp_file_path, "w") as f:
        f.write(
            structure_def.model_dump_json(indent=2, by_alias=True, exclude_none=True)
        )
    # return structure template file
    return FileResponse(
        path=temp_file_path,
        media_type="application/octet-stream",
        filename=temp_file_name,
    )


@router.post("/{id}/structure", status_code=status.HTTP_201_CREATED)
async def upload_structure_definition(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    file: Annotated[
        UploadFile, File(description="JSON file containing the text's structure")
    ],
) -> None:
    """
    Upload the structure definition for a text to apply as a structure of nodes
    """
    # test upload file MIME type
    if not file.content_type.lower() == "application/json":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file MIME type (must be 'application/json')",
        )
    # find text
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )
    # does text already have structure nodes defined?
    if await NodeDocument.find_one(NodeDocument.text_id == text_id).exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This text already has structure nodes",
        )
    # validate structure definition
    try:
        structure_def = TextStructureDefinition.model_validate_json(await file.read())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid structure definition",
        )
    # import nodes depth-first
    nodes = [
        dict(
            level=0,
            position=i,
            parent_id=None,
            **structure_def.nodes[i].model_dump(by_alias=False),
        )
        for i in range(len(structure_def.nodes))
    ]
    structure_def = None
    positions = [0] * len(text.levels)
    positions[0] += len(nodes) - 1
    while nodes:
        node = nodes.pop(0)
        node["id"] = (
            await NodeDocument(
                text_id=text_id,
                label=node["label"],
                level=node["level"],
                position=node["position"],
                parent_id=node["parent_id"],
            ).create()
        ).id
        children_level = node["level"] + 1
        if children_level >= len(text.levels):
            continue
        for child in node.get("nodes", []):
            nodes.append(
                dict(
                    level=children_level,
                    parent_id=node["id"],
                    position=positions[children_level],
                    **child,
                )
            )
            positions[children_level] += 1


@router.post(
    "/{id}/level/{index}", response_model=TextRead, status_code=status.HTTP_200_OK
)
async def insert_level(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    index: Annotated[
        int,
        Path(ge=0, lt=32, description="Index to insert the level at"),
    ],
    translations: Annotated[
        List[StructureLevelTranslation],
        Body(min_length=1, description="Label translations for this level"),
    ],
) -> TextRead:
    text_doc: TextDocument = await TextDocument.get(text_id)

    # text exists?
    if not text_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )

    # index valid?
    if index < 0 or index > len(text_doc.levels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid level index {index}: "
                f"Text has {len(text_doc.levels)} levels."
            ),
        )

    # update text itself
    text_doc.levels.insert(index, translations)
    if text_doc.default_level >= index:
        text_doc.default_level += 1
    await text_doc.save()

    # update all existing layers with level >= index
    await LayerBaseDocument.find(
        LayerBaseDocument.text_id == text_id,
        LayerBaseDocument.level >= index,
        with_children=True,
    ).inc({LayerBaseDocument.level: 1})

    # update all existing nodes with level >= index
    await NodeDocument.find(
        NodeDocument.text_id == text_id, NodeDocument.level >= index
    ).inc({NodeDocument.level: 1})

    # create one dummy node per node on parent level and configure
    # parent-child-relationships on next lower/higher level
    # (different operation if level == 0, as in this case there is no parent level)
    label_prefix = next(
        (
            lvl_trans
            for lvl_trans in translations
            if lvl_trans.get("locale", None) == "enUS"
        ),
        translations[0],
    ).get("label", "???")
    if index == 0:
        dummy_node = NodeDocument(
            text_id=text_id,
            parent_id=None,
            level=index,
            position=0,
            label=f"{label_prefix} 1",
        )
        await dummy_node.create()
        # make dummy node parent of all nodes on level "index+1" (if exists)
        await NodeDocument.find(
            NodeDocument.text_id == text_id, NodeDocument.level == index + 1
        ).update(Set({NodeDocument.parent_id: dummy_node.id}))
    else:
        parent_level_nodes = (
            await NodeDocument.find(
                NodeDocument.text_id == text_id,
                NodeDocument.level == index - 1,
            )
            .sort(+NodeDocument.position)
            .to_list()
        )
        # index > 0, so there is a parent level
        for parent_level_node in parent_level_nodes:
            # parent of each dummy node is respective node on parent level
            dummy_node = NodeDocument(**parent_level_node.model_dump(exclude={"id"}))
            dummy_node.parent_id = parent_level_node.id
            dummy_node.level = index
            dummy_node.position = parent_level_node.position
            dummy_node.label = f"{label_prefix} {parent_level_node.position + 1}"
            await dummy_node.create()
            # make dummy node parent of respective nodes on level "index+1" (if exists)
            # that were previously children of dummy's parent node on level "index-1"
            await NodeDocument.find(
                NodeDocument.text_id == text_id,
                NodeDocument.level == index + 1,
                NodeDocument.parent_id == parent_level_node.id,
            ).update(Set({NodeDocument.parent_id: dummy_node.id}))

    return text_doc


@router.delete(
    "/{id}/level/{index}",
    response_model=TextRead,
    status_code=status.HTTP_200_OK,
)
async def delete_level(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    index: Annotated[
        int,
        Path(ge=0, lt=32, description="Index to insert the level at"),
    ],
) -> TextRead:
    text_doc: TextDocument = await TextDocument.get(text_id)

    # text exists?
    if not text_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )

    # index valid?
    if index < 0 or index >= len(text_doc.levels):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid level index {index}: "
                f"Text has {len(text_doc.levels)} levels."
            ),
        )

    # make nodes of higher level (if exists) parents of nodes of lower level (if exists)
    if index == 0:
        # the level to delete is the highest (lowest index) level, so all nodes on
        # the next lower (higher index) level have no parent node anymore
        await NodeDocument.find(
            NodeDocument.text_id == text_id,
            NodeDocument.level == index + 1,
        ).update(Unset({NodeDocument.parent_id: None}))
    elif index < len(text_doc.levels) - 1:
        # the level to delete is neither the highest (lowest index) nor the
        # lowest (highest index), so need to connect the adjacent levels' nodes
        target_level_nodes = await NodeDocument.find(
            NodeDocument.text_id == text_id,
            NodeDocument.level == index,
        ).to_list()
        for target_level_node in target_level_nodes:
            target_children = await NodeDocument.find(
                NodeDocument.text_id == text_id,
                NodeDocument.level == index + 1,
                NodeDocument.parent_id == target_level_node.id,
            ).to_list()
            for target_child in target_children:
                lbl = f"{target_child.label[:128]} ({target_level_node.label[:125]})"
                target_child.label = lbl[:256]
                target_child.parent_id = target_level_node.parent_id
                await target_child.save()

    # delete all existing layers with level == index
    await LayerBaseDocument.find(
        LayerBaseDocument.text_id == text_id,
        LayerBaseDocument.level == index,
        with_children=True,
    ).delete()

    # update all existing layers with level > index
    await LayerBaseDocument.find(
        LayerBaseDocument.text_id == text_id,
        LayerBaseDocument.level > index,
        with_children=True,
    ).inc({LayerBaseDocument.level: -1})

    # delete all existing nodes with level == index
    await NodeDocument.find(
        NodeDocument.text_id == text_id, NodeDocument.level == index
    ).delete()

    # update all existing nodes with level >= index
    await NodeDocument.find(
        NodeDocument.text_id == text_id, NodeDocument.level >= index
    ).inc({LayerBaseDocument.level: -1})

    # update text itself
    text_doc.levels.pop(index)
    if text_doc.default_level >= index:
        levels_range = range(len(text_doc.levels))
        dl = text_doc.default_level
        # try (in this order): lower level, higher level, 0
        text_doc.default_level = (
            dl - 1
            if dl - 1 in levels_range
            else dl + 1
            if dl + 1 in levels_range
            else 0
        )
    await text_doc.save()

    return text_doc


@router.get("/{id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def get_text(text_id: Annotated[PydanticObjectId, Path(alias="id")]) -> TextRead:
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find text with ID {text_id}",
        )
    return text


@router.patch("/{id}", response_model=TextRead, status_code=status.HTTP_200_OK)
async def update_text(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: TextUpdate,
) -> dict:
    text = await TextDocument.get(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text {text_id} doesn't exist",
        )
    await text.apply(updates.model_dump(exclude_unset=True))
    return await TextDocument.get(text_id)
