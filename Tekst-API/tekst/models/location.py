from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    Field,
    StringConstraints,
)

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)


class Location(ModelBase, ModelFactoryMixin):
    """A location in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text this location belongs to",
        ),
    ]
    parent_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="ID of parent location",
        ),
    ] = None
    level: Annotated[
        int,
        Field(
            ge=0,
            lt=32,
            description="Index of structure level this location is on",
        ),
    ]
    position: Annotated[
        int,
        Field(
            ge=0,
            description="Position among all text locations on this level",
        ),
    ]
    label: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=256,
            strip_whitespace=True,
        ),
        Field(
            description="Label for identifying this text location in level context",
        ),
    ]


class LocationDocument(Location, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "locations"
        indexes = [
            "text_id",
            "parent_id",
            "level",
            "position",
        ]


LocationCreate = Location.create_model()
LocationRead = Location.read_model()
LocationUpdate = Location.update_model()


class DeleteLocationResult(ModelBase):
    contents: int
    locations: int
