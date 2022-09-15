from bson.objectid import ObjectId
from pydantic import Field, validator
from textrig.models.common import AllOptional, BaseModel, ObjectInDB, PyObjectId
from textrig.utils.strings import safe_name


# === TEXT UNIT ===


class Unit(BaseModel):
    """A unit of text (e.g. chapter, paragraph, ...)"""

    text: PyObjectId = Field(..., description="ID of text this unit belongs to")
    level: int = Field(..., description="Index of structure level this unit is on")
    index: int = Field(..., description="Position among all text units on this level")
    label: str = Field(..., description="Label for identifying this text unit")
    parent: PyObjectId | None = Field(None, description="ID of parent unit")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


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
    safe_title: str = Field(
        "text_title",
        min_length=3,
        max_length=32,
        description="Will be ignored and populated automatically",
    )
    subtitle: str | None = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(list(), min_items=1)

    loc_delim: str | None = Field(
        None,
        description="Delimiter for displaying text locations",
    )

    @validator("safe_title", always=True)
    def generate_safe_title(cls, value, values) -> str:
        if not values.get("title"):
            return value
        # swallow_chars and strip_prefix for MongoDB collection naming constraints
        return safe_name(
            values["title"],
            min_len=3,
            max_len=32,
            swallow_chars="$",
            remove_prefix="system.",
        )


class TextUpdate(Text, metaclass=AllOptional):

    pass


class TextInDB(Text, ObjectInDB):

    pass
