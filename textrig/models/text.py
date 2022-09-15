from pydantic import Field, validator
from textrig.models.common import AllOptional, BaseModel, IDModelMixin
from textrig.utils.strings import safe_name


# === TEXT LEVEL ===


class TextLevelCreate(BaseModel):
    label: str


class TextLevelUpdate(BaseModel):
    label: str | None


class TextLevel(TextLevelCreate):
    pass


# === TEXT ===


class TextCreate(BaseModel):
    title: str
    subtitle: str = None
    levels: list[TextLevel] = Field(..., min_items=1, allow_mutation=False)
    safe_title: str | None = Field(
        None, description="Will be ignored and populated automatically"
    )

    @validator("safe_title", always=True)
    def populate_safe_title(cls, value, values) -> str:
        if not values.get("title"):
            return None
        return safe_name(values["title"])

    class Config:
        validate_assignment = True


class TextUpdate(TextCreate, metaclass=AllOptional):
    pass


class Text(TextCreate, IDModelMixin):
    pass


# === TEXT UNIT ===


class TextUnitCreate(BaseModel):
    location: str


class TextUnitUpdate(TextUnitCreate, metaclass=AllOptional):
    pass


class TextUnit(TextUnitCreate, IDModelMixin):
    pass
