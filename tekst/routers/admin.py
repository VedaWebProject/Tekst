from fastapi import APIRouter, Depends, status

from tekst.auth import User, UserRead, get_current_superuser
from tekst.config import TekstConfig, get_config
from tekst.layer_types import get_layer_type_names
from tekst.models.layer import LayerBaseDocument
from tekst.models.platform import PlatformStats, TextStats
from tekst.models.text import NodeDocument, TextDocument


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
    # dependencies=[],
    dependencies=[Depends(get_current_superuser)],
)


# ROUTES DEFINITIONS...


@router.get("/stats", response_model=PlatformStats, status_code=status.HTTP_200_OK)
async def get_stats(cfg: TekstConfig = Depends(get_config)) -> PlatformStats:
    layer_type_names = get_layer_type_names()
    texts = await TextDocument.find_all().to_list()
    text_stats = []

    for text in texts:
        nodes_count = await NodeDocument.find(NodeDocument.text_id == text.id).count()
        layer_types = {
            lt_name: (
                await LayerBaseDocument.find(
                    LayerBaseDocument.text_id == text.id,
                    LayerBaseDocument.layer_type == lt_name,
                    with_children=True,
                ).count()
            )
            for lt_name in layer_type_names
        }
        layers_count = sum(layer_types.values())
        text_stats.append(
            TextStats(
                id=text.id,
                nodes_count=nodes_count,
                layers_count=layers_count,
                layer_types=layer_types,
            )
        )

    return PlatformStats(
        users_count=await User.find_all().count(),
        texts=text_stats,
    )


@router.get("/users", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users(cfg: TekstConfig = Depends(get_config)) -> list[User]:
    return await User.find_all().to_list()
