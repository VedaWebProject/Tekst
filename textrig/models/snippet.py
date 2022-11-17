from pydantic import Field, validator
from textrig.models.common import AllOptional, DbDocument, TextRigBaseModel
from textrig.utils.strings import safe_name


# === TEXT ===


class Snippet(TextRigBaseModel):
    """A content snippet"""

    name: str = Field(..., description="Safe name to identify the snippet by")
    html: str = Field("", description="HTML content of this snippet")

    @validator("name")
    def generate_safe_name(cls, value, values) -> str:
        return safe_name(value, min_len=3, max_len=32)


class SnippetRead(Snippet, DbDocument):
    """An existing content snippet read from the database"""

    ...


class SnippetUpdate(Snippet, DbDocument, metaclass=AllOptional):
    """An update to an existing content snippet"""

    ...
