import random

from datetime import timedelta
from typing import Annotated

from beanie.operators import Eq
from fastapi import APIRouter, Query, status
from pydantic import conint

from tekst.auth import SuperuserDep
from tekst.models.content import ContentBaseDocument


router = APIRouter(
    prefix="/dev",
    include_in_schema=False,
)


@router.get(
    "/fill-archive",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def dev_fill_archive(
    su: SuperuserDep,
    copies_per_content: Annotated[
        conint(ge=1, le=10000),
        Query(alias="n"),
    ] = 100,
):  # pragma: no cover
    """
    Creates n archived copies of each unarchived content in the "contents"
    collection for testing purposes. Only present during development!
    """
    stack = []
    async for content in ContentBaseDocument.find(
        Eq(ContentBaseDocument.archived, False),
        with_children=True,
    ):
        print(
            f"Creating {copies_per_content} archived copies of content {content.id} ..."
        )
        for i in range(copies_per_content):
            stack.append(
                content.model_copy(
                    update={
                        "id": None,
                        "created_at": (
                            content.created_at
                            - timedelta(
                                days=random.randint(
                                    1,
                                    copies_per_content * 100,
                                )
                            )
                        ),
                        "archived": True,
                    }
                )
            )
            if len(stack) > 5000:
                await ContentBaseDocument.insert_many(stack)
                stack = []
    if stack:
        await ContentBaseDocument.insert_many(stack)
