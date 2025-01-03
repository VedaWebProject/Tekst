from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
    PydanticObjectId,
)
from tekst.utils import validators as val


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
        str,
        Field(
            description="Content of the correction note",
        ),
        StringConstraints(
            min_length=1,
            max_length=1000,
            strip_whitespace=True,
        ),
        val.CleanupMultiline,
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
        datetime,
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
