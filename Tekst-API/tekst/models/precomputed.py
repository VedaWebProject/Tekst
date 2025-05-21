from datetime import UTC, datetime
from typing import Annotated, Any

from beanie import PydanticObjectId
from pydantic import AwareDatetime, Field

from tekst.models.common import DocumentBase, ModelBase
from tekst.types import ConStr


class PrecomputedDataDocument(ModelBase, DocumentBase):
    """Base model for precomputed data"""

    class Settings(DocumentBase.Settings):
        name = "precomputed"
        indexes = [
            "precomputed_type",
            "ref_id",
        ]

    ref_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the resource this precomputed data refers to",
        ),
    ]

    precomputed_type: Annotated[
        ConStr(
            max_length=64,
        ),
        Field(
            description="String identifying the type of precomputed data",
        ),
    ]

    created_at: Annotated[
        AwareDatetime,
        Field(
            description="The time this data was created",
        ),
    ] = datetime.fromtimestamp(0, UTC)

    data: Annotated[
        Any | None,
        Field(
            description="The precomputed data",
        ),
    ] = None
