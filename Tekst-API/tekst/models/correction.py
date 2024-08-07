from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from tekst.models.common import (
    DocumentBase,
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
    user_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the user who created the correction note",
        ),
    ]
    position: Annotated[
        int,
        Field(
            description="Position of the content this correction refers to",
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
    date: Annotated[
        datetime,
        Field(
            description="Date when the correction was created",
        ),
    ]
    location_labels: Annotated[
        list[str],
        Field(
            description="Text location labels from root to target location",
        ),
    ]


class CorrectionCreate(ModelBase):
    resource_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the resource this correction refers to",
        ),
    ]
    position: Annotated[
        int,
        Field(
            description="Position of the content this correction refers to",
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


class CorrectionDocument(Correction, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "corrections"
        indexes = [
            "resource_id",
            "position",
        ]


CorrectionRead = Correction.read_model()
