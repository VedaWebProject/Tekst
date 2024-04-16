from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from tekst.models.common import ModelBase, PydanticObjectId
from tekst.models.location import LocationRead
from tekst.resources import AnyContentRead


class LocationDefinition(ModelBase):
    label: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=256,
            strip_whitespace=True,
        ),
    ]
    locations: list["LocationDefinition"] | None = None


class TextStructureImportData(ModelBase):
    model_config = ConfigDict(extra="allow")
    locations: list[LocationDefinition] = []


class LocationData(ModelBase):
    location_path: list[LocationRead] = []
    contents: Annotated[
        list[AnyContentRead],
        Field(
            discriminator="resource_type",
        ),
    ] = []


class ResourceImportData(ModelBase):
    resource_id: PydanticObjectId
    contents: list[dict] = []
