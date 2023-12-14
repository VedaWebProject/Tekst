from fastapi import APIRouter, HTTPException, Response, status

from tekst.auth import SuperuserDep
from tekst.email import send_test_email
from tekst.models.node import NodeDocument
from tekst.models.platform import PlatformStats, TextStats
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument, UserRead
from tekst.resource_types import resource_types_mgr


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# ROUTES DEFINITIONS...


@router.get("/stats", response_model=PlatformStats, status_code=status.HTTP_200_OK)
async def get_stats(su: SuperuserDep) -> PlatformStats:
    resource_type_names = resource_types_mgr.list_names()
    texts = await TextDocument.find_all().to_list()
    text_stats = []

    for text in texts:
        nodes_count = await NodeDocument.find(NodeDocument.text_id == text.id).count()
        resource_types = {
            lt_name: (
                await ResourceBaseDocument.find(
                    ResourceBaseDocument.text_id == text.id,
                    ResourceBaseDocument.resource_type == lt_name,
                    with_children=True,
                ).count()
            )
            for lt_name in resource_type_names
        }
        resources_count = sum(resource_types.values())
        text_stats.append(
            TextStats(
                id=text.id,
                nodes_count=nodes_count,
                resources_count=resources_count,
                resource_types=resource_types,
            )
        )

    return PlatformStats(
        users_count=await UserDocument.find_all().count(),
        texts=text_stats,
    )


@router.get("/users", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users(su: SuperuserDep) -> list[UserDocument]:
    return await UserDocument.find_all().to_list()


@router.get(
    "/testemail",
    summary="Send test email to test email setup",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def test_email(su: SuperuserDep):
    try:
        send_test_email(su)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
