from pydantic import Field, validator
from textrig.models.common import AllOptional, BaseModel, ObjectInDB, PyObjectId
from textrig.utils.strings import safe_name
from uuid import uuid4


# === TEXT UNIT ===


class Unit(BaseModel):
    """A unit of text (e.g. chapter, paragraph, ...)"""

    text: PyObjectId = Field(..., description="ID of text this unit belongs to")
    level: int = Field(..., description="Index of structure level this unit is on")
    index: int = Field(..., description="Position among all text units on this level")
    label: str = Field(..., description="Label for identifying this text unit")
    parent: PyObjectId | None = Field(None, description="ID of parent unit")


class UnitUpdate(Unit, metaclass=AllOptional):

    pass


class UnitInDB(Unit, ObjectInDB):

    pass


# === TEXT ===


class Text(BaseModel):
    """A text represented in TextRig"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )
    subtitle: str | None = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    slug: str = Field(
        None,
        min_length=3,
        max_length=32,
        description="Will be ignored and populated automatically",
    )

    levels: list[str] = Field(list(), min_items=1)

    loc_delim: str | None = Field(
        None,
        description="Delimiter for displaying text locations",
    )

    @validator("slug", always=True)
    def generate_slug(cls, value, values) -> str:
        if not value:
            if not values.get("title", None):
                return str(uuid4())
            else:
                return safe_name(values.get("title"), min_len=3, max_len=32)
        else:
            return value

    class Config:
        schema_extra = {
            "example": {
                "title": "Rigveda",
                "subtitle": "An ancient Indian collection of Vedic Sanskrit hymns",
                "levels": ["Book", "Hymn", "Stanza"],
                "locDelim": "."
            }
        }


class TextUpdate(Text, metaclass=AllOptional):

    pass


class TextInDB(Text, ObjectInDB):

    pass
