from fastapi import APIRouter, HTTPException, status
from textrig.config import TextRigConfig, get_config
from textrig.models.foo import FooCreate, FooDocument, FooRead, FooUpdate


_cfg: TextRigConfig = get_config()


router = APIRouter(
    prefix="/foos",
    tags=["foos"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("", response_model=list[FooRead], status_code=status.HTTP_200_OK)
async def get_all_foos(limit: int = 100) -> list[FooRead]:
    return await FooDocument.find_all(limit=limit).project(FooRead).to_list()


@router.post("", response_model=FooRead, status_code=status.HTTP_201_CREATED)
async def create_foo(foo: FooCreate) -> FooRead:
    return await FooDocument.from_(foo).create()


@router.patch("", response_model=FooRead, status_code=status.HTTP_200_OK)
async def update_foo(foo_update: FooUpdate) -> FooRead:
    foo: FooDocument = await FooDocument.get(foo_update.id)
    if not foo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Foo with ID {foo_update.id} doesn't exist",
        )
    await foo.set(foo_update.dict(exclude={"id"}, exclude_unset=True))
    return foo
