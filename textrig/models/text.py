from pydantic import Field
from textrig.models.common import AllOptional, BaseModel, IDModelMixin


# === TEXT LEVEL ===


class TextLevelCreate(BaseModel):
    label: str


class TextLevelUpdate(BaseModel):
    label: str | None


class TextLevel(TextLevelCreate, IDModelMixin):
    pass


# === TEXT ===


class TextCreate(BaseModel):
    title: str
    subtitle: str | None
    levels: list[TextLevel] = Field(..., min_items=1, allow_mutation=False)

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
