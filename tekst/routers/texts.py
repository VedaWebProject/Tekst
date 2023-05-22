from beanie.operators import Or
from fastapi import APIRouter, HTTPException, status

from tekst.auth import SuperuserDep
from tekst.models.common import PyObjectId
from tekst.models.text import TextCreate, TextDocument, TextRead, TextUpdate


router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[TextRead], status_code=status.HTTP_200_OK)
async def get_all_texts(limit: int = 100) -> list[TextRead]:
    return await TextDocument.find_all(limit=limit).project(TextRead).to_list()


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
    return text
