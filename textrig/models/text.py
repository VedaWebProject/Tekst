from fastapi import HTTPException, status
from pydantic import Field, root_validator
from textrig.db.io import DbIO
from textrig.logging import log
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)
from textrig.utils.strings import safe_name


class Text(TextRigBaseModel):
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

    subtitle: str = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(..., min_items=1)

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

    async def create(self, db_io: DbIO) -> "TextRead":
        text = self.ensure_model_type(Text)
        if await db_io.find_one("texts", text.slug, "slug"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A text with an equal slug already exists",
            )
        text_read = TextRead(**await db_io.insert_one("texts", text))
        log.debug(f"Created text: {text_read}")
        return text_read


class TextRead(Text, DbDocument):
    """An existing text read from the database"""

    @classmethod
    async def read(cls, doc_id: str | DocumentId, db_io: DbIO) -> "TextRead":
        text = await db_io.find_one("texts", doc_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A text with ID {str(doc_id)} cannot be found",
            )
        return TextRead(**text)


class TextUpdate(Text, DbDocument, metaclass=AllOptional):
    """An update to an existing text"""

    async def update(self, db_io: DbIO) -> TextRead:
        text_update = self.ensure_model_type(TextUpdate)
        updated_id = await db_io.update("texts", text_update)
        if not updated_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not update text {text_update.id}",
            )
        log.debug(f"Updated text {updated_id}: {text_update.dict()}")
        return TextRead(**await db_io.find_one("texts", updated_id))


class Node(TextRigBaseModel):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_slug: str = Field(..., description="Slug of the text this node belongs to")
    parent_id: DocumentId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    index: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    async def create(self, db_io: DbIO) -> "NodeRead":
        node = self.ensure_model_type(Node)
        # find text the node belongs to
        text = await db_io.find_one("texts", node.text_slug, field="slug")
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Corresponding text '{node.text_slug}' does not exist",
            )
        # check for semantic duplicates
        dupes = await db_io.find_one_by_example(
            "nodes",
            {"text_slug": node.text_slug, "level": node.level, "index": node.index},
        )
        if dupes:
            log.warning(f"Cannot create node. Conflict: {node}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict with existing node",
            )
        return NodeRead(**await db_io.insert_one("nodes", node))


class NodeRead(Node, DbDocument):
    """An existing node read from the database"""

    @classmethod
    async def read(cls, doc_id: str | DocumentId, db_io: DbIO) -> "NodeRead":
        node = await db_io.find_one("texts", doc_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A node with ID {str(doc_id)} cannot be found",
            )
        return NodeRead(**node)


class NodeUpdate(Node, DbDocument, metaclass=AllOptional):
    """An update to an existing node"""

    async def update(self, db_io: DbIO) -> NodeRead:
        node_update = self.ensure_model_type(NodeUpdate)
        updated_id = await db_io.update("nodes", node_update)
        if not updated_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not update node {node_update.id}",
            )
        log.debug(f"Updated node {updated_id}: {node_update.dict()}")
        return NodeRead(**await db_io.find_one("nodes", updated_id))
