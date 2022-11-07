from pydantic import Field
from textrig.models.common import AllOptional, ObjectInDB
from textrig.models.layer import UnitTypeBase


class UnitType(UnitTypeBase):
    """A simple fulltext unit type"""

    text: str = Field(None, description="Text content of the fulltext unit")

    def get_template() -> dict:
        return {"text": None}


class UnitTypeRead(UnitType, ObjectInDB):

    ...


class UnitTypeUpdate(UnitType, metaclass=AllOptional):

    ...
