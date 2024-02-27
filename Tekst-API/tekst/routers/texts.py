from copy import deepcopy
from tempfile import NamedTemporaryFile
from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In, Or, Set, Unset
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Path,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from tekst import errors
from tekst.auth import OptionalUserDep, SuperuserDep
from tekst.utils import get_temp_dir
from tekst.logging import log
from tekst.models.common import Translations
from tekst.models.content import ContentBaseDocument
from tekst.models.exchange import LocationDefinition, TextStructureImportData
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import (
    TextCreate,
    TextDocument,
    TextLevelTranslation,
    TextRead,
    TextUpdate,
)
from tekst.settings import get_settings


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(ou: OptionalUserDep, limit: int = 128) -> list[TextRead]:
    """
    Returns a list of all texts.
    Only users with admin permissions will see inactive texts.
    """
    restrictions = {} if (ou and ou.is_superuser) else {"is_active": True}
    return await TextDocument.find(restrictions).limit(limit).to_list()


@router.post(
    "",
    response_model=TextRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_TEXT_SAME_TITLE_OR_SLUG,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def create_text(su: SuperuserDep, text: TextCreate) -> TextRead:
    if await TextDocument.find_one(
        Or({"title": text.title}, {"slug": text.slug})
    ).exists():
        raise errors.E_409_TEXT_SAME_TITLE_OR_SLUG
    return await TextDocument.model_from(text).create()


@router.get(
    "/{id}/template",
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
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
        raise errors.E_404_TEXT_NOT_FOUND
    # create template for text
    structure_def: TextStructureImportData = TextStructureImportData()
    curr_location_def: LocationDefinition | None = None
    dummy_location = LocationDefinition(
        label="Label for the first location on level '{}' (required!)",
    )
    for n in range(len(text.levels)):
        location = deepcopy(dummy_location)
        location.label = location.label.format(text.levels[n][0]["translation"])
        if curr_location_def is None:
            structure_def.locations.append(location)
        else:
            curr_location_def.locations = []
            curr_location_def.locations.append(location)
        curr_location_def = location
    # validate template
    try:
        TextStructureImportData.model_validate(structure_def)
    except Exception:  # pragma: no cover
        raise errors.E_500_INTERNAL_SERVER_ERROR
    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")
    tempfile.write(
        structure_def.model_dump_json(indent=2, by_alias=True, exclude_none=True)
    )
    tempfile.flush()
    # prepare headers
    filename = f"{text.slug}_structure_template.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    # return structure template file
    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        path=tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


@router.post(
    "/{id}/structure",
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_409_TEXT_IMPORT_LOCATIONS_EXIST,
            errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON,
            errors.E_400_UPLOAD_INVALID_JSON,
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def import_text_structure(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    file: Annotated[
        UploadFile, File(description="JSON file containing the text's structure")
    ],
) -> None:
    """
    Upload the structure definition for a text to apply as a structure of locations
    """
    # test upload file MIME type
    if not file.content_type.lower() == "application/json":
        raise errors.E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON
    # find text
    text = await TextDocument.get(text_id)
    if not text:
        raise errors.E_404_TEXT_NOT_FOUND
    # does text already have locations defined?
    if await LocationDocument.find_one(LocationDocument.text_id == text_id).exists():
        raise errors.E_409_TEXT_IMPORT_LOCATIONS_EXIST
    # validate structure definition
    try:
        structure_def = TextStructureImportData.model_validate_json(await file.read())
    except Exception:
        raise errors.E_400_UPLOAD_INVALID_JSON
    # import locations depth-first
    locations = structure_def.model_dump(exclude_none=True, by_alias=False)["locations"]
    structure_def = None  # de-reference structure definition object
    # apply parent IDs (None) to all 0-level locations
    for location in locations:
        location["parent_id"] = None
    # process locations level by level
    for level in range(len(text.levels)):
        if len(locations) == 0:
            break  # pragma: no cover
        # create LocationDocument instances for each location definition
        location_docs = [
            LocationDocument(
                text_id=text_id,
                parent_id=locations[i]["parent_id"],
                level=level,
                position=i,
                label=locations[i]["label"],
            )
            for i in range(len(locations))
        ]
        # bulk-insert documents
        inserted_ids = (await LocationDocument.insert_many(location_docs)).inserted_ids
        # collect children and their parents' IDs
        children = []
        for i in range(len(locations)):
            children_temp = locations[i].get("locations", [])
            # apply parent ID
            for c in children_temp:
                c["parent_id"] = inserted_ids[i]
            children += children_temp
        locations = children


@router.post(
    "/{id}/level/{index}",
    response_model=TextRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_400_INVALID_LEVEL,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def insert_level(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    index: Annotated[
        int,
        Path(ge=0, lt=32, description="Index to insert the level at"),
    ],
    translations: Annotated[
        Translations[TextLevelTranslation],
        Body(description="Label translations for this level", min_length=1),
    ],
) -> TextRead:
    text_doc: TextDocument = await TextDocument.get(text_id)

    if not text_doc:
        raise errors.E_404_TEXT_NOT_FOUND

    # index valid?
    if index < 0 or index > len(text_doc.levels):
        raise errors.E_400_INVALID_LEVEL

    # update text itself
    text_doc.levels.insert(index, translations)
    if text_doc.default_level >= index:
        text_doc.default_level += 1
    await text_doc.save()

    # update all existing resources with level >= index
    await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id,
        ResourceBaseDocument.level >= index,
        with_children=True,
    ).inc({ResourceBaseDocument.level: 1})

    # update all existing locations with level >= index
    await LocationDocument.find(
        LocationDocument.text_id == text_id, LocationDocument.level >= index
    ).inc({LocationDocument.level: 1})

    # create one dummy location per location on parent level and configure
    # parent-child-relationships on next lower/higher level
    # (different operation if level == 0, as in this case there is no parent level)
    translations_map = {t.get("locale"): t.get("translation") for t in translations}
    label_prefix = (
        translations_map.get("*")
        or translations_map.get("enUS")
        or list(translations_map.values())[0]
        or "???"
    )
    if index == 0:
        dummy_location = LocationDocument(
            text_id=text_id,
            parent_id=None,
            level=index,
            position=0,
            label=f"{label_prefix} 1",
        )
        await dummy_location.create()
        # make dummy location parent of all locations on level "index+1" (if exists)
        await LocationDocument.find(
            LocationDocument.text_id == text_id, LocationDocument.level == index + 1
        ).update(Set({LocationDocument.parent_id: dummy_location.id}))
    else:
        parent_level_locations = (
            await LocationDocument.find(
                LocationDocument.text_id == text_id,
                LocationDocument.level == index - 1,
            )
            .sort(+LocationDocument.position)
            .to_list()
        )
        # index > 0, so there is a parent level
        for parent_level_location in parent_level_locations:
            # parent of each dummy location is respective location on parent level
            dummy_location = LocationDocument(
                **parent_level_location.model_dump(exclude={"id"})
            )
            dummy_location.parent_id = parent_level_location.id
            dummy_location.level = index
            dummy_location.position = parent_level_location.position
            dummy_location.label = (
                f"{label_prefix} {parent_level_location.position + 1}"
            )
            await dummy_location.create()
            # make dummy location parent of respective locations on level "index+1"
            # that were children of dummy's parent location on level "index-1"
            await LocationDocument.find(
                LocationDocument.text_id == text_id,
                LocationDocument.level == index + 1,
                LocationDocument.parent_id == parent_level_location.id,
            ).update(Set({LocationDocument.parent_id: dummy_location.id}))

    return text_doc


@router.delete(
    "/{id}/level/{index}",
    response_model=TextRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_400_INVALID_LEVEL,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
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

    if not text_doc:
        raise errors.E_404_TEXT_NOT_FOUND

    # index valid?
    if index < 0 or index >= len(text_doc.levels):
        raise errors.E_400_INVALID_LEVEL

    # make locations of higher level (if it exists)
    # parents of locations of lower level (if it exists)
    if index == 0:
        # the level to delete is the highest (lowest index) level, so all locations on
        # the next lower (higher index) level have no parent location anymore
        await LocationDocument.find(
            LocationDocument.text_id == text_id,
            LocationDocument.level == index + 1,
        ).update(Unset({LocationDocument.parent_id: None}))
    elif index < len(text_doc.levels) - 1:
        # the level to delete is neither the highest (lowest index) nor the
        # lowest (highest index), so need to connect the adjacent levels' locations
        target_level_locations = await LocationDocument.find(
            LocationDocument.text_id == text_id,
            LocationDocument.level == index,
        ).to_list()
        for target_level_location in target_level_locations:
            target_children = await LocationDocument.find(
                LocationDocument.text_id == text_id,
                LocationDocument.level == index + 1,
                LocationDocument.parent_id == target_level_location.id,
            ).to_list()
            for target_child in target_children:
                lbl = (
                    f"{target_child.label[:128]} ({target_level_location.label[:125]})"
                )
                target_child.label = lbl[:256]
                target_child.parent_id = target_level_location.parent_id
                await target_child.save()

    # delete all existing resources with level == index
    await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id,
        ResourceBaseDocument.level == index,
        with_children=True,
    ).delete()

    # update all existing resources with level > index
    await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id,
        ResourceBaseDocument.level > index,
        with_children=True,
    ).inc({ResourceBaseDocument.level: -1})

    # delete all existing locations with level == index
    await LocationDocument.find(
        LocationDocument.text_id == text_id, LocationDocument.level == index
    ).delete()

    # update all existing locations with level >= index
    await LocationDocument.find(
        LocationDocument.text_id == text_id, LocationDocument.level >= index
    ).inc({ResourceBaseDocument.level: -1})

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


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_400_TEXT_DELETE_LAST_TEXT,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_text(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    text = await TextDocument.get(text_id)
    if not text:
        raise errors.E_404_TEXT_NOT_FOUND
    if await TextDocument.find_all().count() <= 1:
        raise errors.E_400_TEXT_DELETE_LAST_TEXT
    # get resources associated with target text
    resources = await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id, with_children=True
    ).to_list()
    # delete contents of all resources associated with target text
    await ContentBaseDocument.find(
        In(ContentBaseDocument.resource_id, [resource.id for resource in resources]),
        with_children=True,
    ).delete_many()
    # delete resources associated with target text
    await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id, with_children=True
    ).delete_many()
    # delete locations associated with target text
    await LocationDocument.find(
        LocationDocument.text_id == text_id,
    ).delete_many()
    # delete text itself
    await text.delete()
    # check if deleted text was default text, correct if necessary
    pf_settings_doc = await get_settings()
    if pf_settings_doc.default_text_id == text_id:
        pf_settings_doc.default_text_id = (await TextDocument.find_one()).id
        await pf_settings_doc.replace()


@router.get(
    "/{id}",
    response_model=TextRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
        ]
    ),
)
async def get_text(text_id: Annotated[PydanticObjectId, Path(alias="id")]) -> TextRead:
    text = await TextDocument.get(text_id)
    if not text:
        raise errors.E_404_TEXT_NOT_FOUND
    return text


@router.patch(
    "/{id}",
    response_model=TextRead,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_TEXT_NOT_FOUND,
            errors.E_401_UNAUTHORIZED,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_text(
    su: SuperuserDep,
    text_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: TextUpdate,
) -> TextDocument:
    text = await TextDocument.get(text_id)
    if not text:
        raise errors.E_404_TEXT_NOT_FOUND
    return await text.apply_updates(updates)
