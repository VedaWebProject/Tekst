from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    BeforeValidator,
    Field,
)

from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ReadBase,
    make_update_model,
)
from tekst.types import LocationAlias, LocationLabel, LocationLevel, LocationPosition


class Location(ModelBase):
    """A location in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the text this location belongs to"),
        ExcludeFromModelVariants(update=True),
    ]

    parent_id: Annotated[
        PydanticObjectId | None,
        Field(description="ID of parent location"),
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
        LocationLabel,
        Field(description="Label for identifying this text location in level context"),
    ]

    aliases: Annotated[
        list[LocationAlias] | None,
        Field(
            description="List of aliases for this location",
            min_length=1,
            max_length=16,
        ),
        BeforeValidator(lambda v: v or None),
    ] = None


class LocationDocument(Location, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "locations"
        indexes = [
            [
                "text_id",
                "parent_id",
                "level",
                "position",
                "aliases",
            ]
        ]


class LocationCreate(Location, CreateBase):
    pass


class LocationRead(Location, ReadBase):
    pass


LocationUpdate = make_update_model(Location)


class DeleteLocationResult(ModelBase):
    contents: int
    locations: int


class LocationImport(ModelBase):
    """Model for importing (creating/updating) location data"""

    parent_id: Annotated[
        PydanticObjectId | None,
        Field(description="ID of parent location"),
    ] = None

    level: Annotated[
        LocationLevel,
        Field(description="Index of structure level this location is on"),
    ]

    position: Annotated[
        LocationPosition,
        Field(description="Position among all text locations on this level"),
    ]

    label: Annotated[
        LocationLabel,
        Field(description="Label for identifying this text location in level context"),
    ]

    aliases: Annotated[
        list[LocationAlias] | None,
        Field(description="List of aliases for this location"),
    ] = None
