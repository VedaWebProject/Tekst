from pydantic import Field
from textrig.models.common import AllOptional, ObjectInDB
from textrig.models.unit_base import UnitBase


class Unit(UnitBase):
    """A simple fulltext unit type"""

    text: str = Field(None, description="Text content of the fulltext unit")

    def get_template() -> dict:
        return {"text": None}


class UnitTypeRead(Unit, ObjectInDB):

    ...


class UnitTypeUpdate(Unit, metaclass=AllOptional):

    ...
