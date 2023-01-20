# from fastapi import HTTPException, status
# from textrig.utils.strings import safe_name
from beanie import PydanticObjectId
from pydantic import Field

# from textrig.db.io import DbIO
# from textrig.logging import log
from textrig.models.common import AllOptional, DocumentBase, Metadata


class Text(DocumentBase):
    """A text represented in TextRig"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )

    slug: str = Field(
        ...,
        regex=r"^[a-z][a-z0-9\-_]{0,14}[a-z0-9]$",
        min_length=2,
        max_length=16,
        description=(
            "A short identifier string for use in URLs and internal operations"
        ),
    )

    subtitle: str = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(..., min_items=1)

    loc_delim: str = Field(
        ",",
        description="Delimiter for displaying text locations",
    )

    class Settings:
        name = "texts"

    # @root_validator(pre=True)
    # def generate_dynamic_defaults(cls, values) -> dict:
    #     # generate slug if none is given
    #     if "slug" not in values:
    #         if not values.get("title", None):
    #             values["slug"] = "text"
    #         else:
    #             values["slug"] = safe_name(
    #                 values.get("title"), min_len=2, max_len=16, delim=""
    #             )
    #     return values


class TextUpdate(Text, metaclass=AllOptional):
    """An update to an existing text"""

    pass


class Node(DocumentBase):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: PydanticObjectId = Field(
        ..., description="ID of the text this node belongs to"
    )
    parent_id: PydanticObjectId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    index: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    class Settings:
        name = "nodes"


class NodeUpdate(Node, metaclass=AllOptional):
    """An update to an existing node"""

    pass
