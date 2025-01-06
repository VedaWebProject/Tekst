from typing import Annotated

from beanie import PydanticObjectId
from pydantic import Field

from tekst.models.common import ModelBase
from tekst.models.location import LocationRead
from tekst.resources import AnyContentRead


class LocationData(ModelBase):
    location_path: Annotated[
        list[LocationRead],
        Field(
            description="Path of locations from level 0 to this location",
        ),
    ] = []
    previous_loc_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the preceding location on the same level",
            alias="prev",
        ),
    ] = None
    next_loc_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of the subsequent location on the same level",
            alias="next",
        ),
    ] = None
    contents: Annotated[
        list[AnyContentRead],
        Field(
            description="Contents of various resources on this location",
        ),
    ] = []
