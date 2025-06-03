from typing import Annotated

from pydantic import AwareDatetime, Field

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.types import ConStr


class Correction(ModelBase, ModelFactoryMixin):
    resource_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the resource this correction refers to",
        ),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the location this correction refers to",
        ),
    ]
    note: Annotated[
        ConStr(
            max_length=2000,
            cleanup="multiline",
        ),
        Field(
            description="Content of the correction note",
        ),
    ]
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the user who created the correction note",
        ),
        ExcludeFromModelVariants(create=True),
    ]
    position: Annotated[
        int,
        Field(
            description="Position of the correction on the resource's level",
        ),
        ExcludeFromModelVariants(create=True),
    ]
    date: Annotated[
        AwareDatetime,
        Field(
            description="Date when the correction was created",
        ),
        ExcludeFromModelVariants(create=True),
    ]
    location_labels: Annotated[
        list[str],
        Field(
            description="Text location labels from root to target location",
        ),
        ExcludeFromModelVariants(create=True),
    ]


class CorrectionDocument(Correction, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "corrections"
        indexes = [
            "resource_id",
            "location_id",
        ]


CorrectionCreate = Correction.create_model()
CorrectionRead = Correction.read_model()
