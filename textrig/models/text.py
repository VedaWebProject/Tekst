from typing import List

from pydantic import Field
from textrig.models.common import DbModel
from textrig.utils.strings import safe_name


class TextLevel(DbModel):

    label: str


class Text(DbModel):

    title: str
    subtitle: str | None = None
    levels: List[TextLevel] = Field(..., min_items=1, allow_mutation=False)

    class Config:
        validate_assignment = True


class TextUnit(DbModel):

    location: str
