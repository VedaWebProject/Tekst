from pydantic import Field
from textrig.models.common import AllOptional, DbDocument
from textrig.models.unit import UnitBase


class Unit(UnitBase):
    """A simple fulltext unit type"""

    text: str = Field(None, description="Text content of the fulltext unit")

    def get_template() -> dict:
        return {"text": None}


class UnitTypeRead(Unit, DbDocument):
    """An existing fulltext unit read from the database"""

    ...


class UnitTypeUpdate(Unit, metaclass=AllOptional):
    """An update to an existing fulltext unit"""

    ...
