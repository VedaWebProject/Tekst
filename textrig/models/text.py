from pydantic import Field, root_validator
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


class UnitRead(Unit, ObjectInDB):

    pass


class UnitUpdate(Unit, metaclass=AllOptional):

    pass


# === TEXT ===


class Text(BaseModel):
    """A text represented in TextRig"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )

    slug: str = Field(
        None,
        regex=r"^[a-z][a-z0-9\-_]{0,14}[a-z0-9]$",
        min_length=2,
        max_length=16,
        description=(
            "A short identifier string for use in URLs and internal operations "
            "(will be generated automatically if missing)"
        ),
    )

    subtitle: str | None = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(list(), min_items=1)

    loc_delim: str = Field(
        ",",
        description="Delimiter for displaying text locations",
    )

    @root_validator(pre=True)
    def generate_dynamic_defaults(cls, values) -> dict:
        # generate slug if none is given
        if "slug" not in values:
            if not values.get("title", None):
                values["slug"] = "text"
            else:
                values["slug"] = safe_name(
                    values.get("title"), min_len=2, max_len=16, delim=""
                )

        return values

    class Config:
        schema_extra = {
            "example": {
                "title": "Rigveda",
                "slug": "rigveda",
                "subtitle": "An ancient Indian collection of Vedic Sanskrit hymns",
                "levels": ["Book", "Hymn", "Stanza"],
                "locDelim": ".",
            }
        }


class TextRead(Text, ObjectInDB):

    pass


class TextUpdate(Text, metaclass=AllOptional):

    pass
