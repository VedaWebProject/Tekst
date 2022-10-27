from pydantic import Field
from textrig.models.common import AllOptional, ObjectInDB
from textrig.models.layer import Unit


class FullText(Unit):
    """A simple fulltext unit type"""

    text: str | None = Field(None, description="Text content of the fulltext unit")


class FullTextRead(FullText, ObjectInDB):

    pass


class FullTextUpdate(FullText, metaclass=AllOptional):

    pass
