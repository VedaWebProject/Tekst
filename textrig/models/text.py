from pydantic import Field, validator
from textrig.models.common import AllOptional, BaseModel, ObjectInDB
from textrig.utils.strings import safe_name


# === TEXT UNIT ===


class Unit(BaseModel):

    level: str
    label: str


class UnitUpdate(Unit, metaclass=AllOptional):

    pass


# === TEXT LEVEL ===


class Level(BaseModel):

    label: str


class LevelUpdate(Level, metaclass=AllOptional):

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
    structure: list[Level] = Field(..., min_items=1)

    loc_delim: str | None = Field(
        description="Location delimiter for displaying location of text units",
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
    """Updates to an existing text"""

    pass


class TextInDB(Text, ObjectInDB):

    pass
