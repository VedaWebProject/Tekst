from pydantic import Field, validator
from textrig.models.common import AllOptional, ObjectInDB, TextRigBaseModel
from textrig.utils.strings import safe_name


# === TEXT ===


class Snippet(TextRigBaseModel):
    """A content snippet"""

    name: str = Field(..., description="Safe name to identify the snippet by")
    html: str = Field("", description="HTML content of this snippet")

    @validator("name")
    def generate_safe_name(cls, value, values) -> str:
        return safe_name(value, min_len=3, max_len=32)


class SnippetRead(Snippet, ObjectInDB):

    ...


class SnippetUpdate(Snippet, metaclass=AllOptional):

    ...
