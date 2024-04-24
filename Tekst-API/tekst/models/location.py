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
from tekst.models.text import TextDocument


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

    @classmethod
    async def full_location_labels(
        cls,
        text_id: PydanticObjectId,
        for_level: int | None = None,
    ) -> dict[str, str]:
        """
        Returns the full concatenated location labels for all locations on the
        given level of the text wwith the given ID. Location label parts are delimited
        by the text's location delimiter or ", " if no delimiter is set.
        """
        text = await TextDocument.get(text_id)
        for_level = max(0, for_level) if for_level is not None else len(text.levels) - 1
        loc_delim = text.loc_delim or ", "
        location_labels = {}
        for level in range(for_level + 1):
            location_labels = {
                str(n.id): loc_delim.join(
                    [
                        lbl
                        for lbl in [location_labels.get(str(n.parent_id)), n.label]
                        if lbl
                    ]
                )
                for n in await LocationDocument.find(
                    LocationDocument.text_id == text.id,
                    LocationDocument.level == level,
                )
                .sort(+LocationDocument.position)
                .to_list()
            }
        return location_labels


LocationCreate = Location.create_model()
LocationRead = Location.read_model()
LocationUpdate = Location.update_model()


class DeleteLocationResult(ModelBase):
    contents: int
    locations: int
