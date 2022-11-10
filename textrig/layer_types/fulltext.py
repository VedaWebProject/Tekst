from pydantic import Field
from textrig.models.common import AllOptional, DbDocument
from textrig.models.layer import UnitBase


class FullTextUnit(UnitBase):
    """A simple fulltext layer unit type"""

    text: str = Field(None, description="Text content of the fulltext unit")


class FullTextUnitRead(FullTextUnit, DbDocument):
    """An existing fulltext unit read from the database"""

    ...


class FullTextUnitUpdate(FullTextUnit, metaclass=AllOptional):
    """An update to an existing fulltext unit"""

    ...
