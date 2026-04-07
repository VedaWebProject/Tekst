from typing import Annotated

from pydantic import AwareDatetime, Field, StringConstraints

from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    PydanticObjectId,
    ReadBase,
)
from tekst.types import MultiLineString


class Correction(ModelBase):
    resource_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the resource this correction refers to"),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the location this correction refers to"),
    ]
    note: Annotated[
        str,
        StringConstraints(min_length=1, max_length=2000),
        MultiLineString,
        Field(description="Content of the correction note"),
    ]
    user_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the user who created the correction note"),
        ExcludeFromModelVariants(create=True),
    ]
    position: Annotated[
        int,
        Field(description="Position of the correction on the resource's level"),
        ExcludeFromModelVariants(create=True),
    ]
    date: Annotated[
        AwareDatetime,
        Field(description="Date when the correction was created"),
        ExcludeFromModelVariants(create=True),
    ]
    location_labels: Annotated[
        list[str],
        Field(description="Text location labels from root to target location"),
        ExcludeFromModelVariants(create=True),
    ]


class CorrectionDocument(Correction, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "corrections"
        indexes = [
            [
                "resource_id",
                "location_id",
            ]
        ]


class CorrectionCreate(Correction, CreateBase):
    pass


class CorrectionRead(Correction, ReadBase):
    pass
