from typing import Annotated

from pydantic import Field

from tekst.models.common import ModelBase
from tekst.models.location import LocationRead
from tekst.resources import AnyContentRead


class LocationData(ModelBase):
    location_path: list[LocationRead] = []
    contents: Annotated[
        list[AnyContentRead],
        Field(
            discriminator="resource_type",
        ),
    ] = []
