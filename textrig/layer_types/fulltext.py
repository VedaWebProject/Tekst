from pydantic import Field
from textrig.layer_types import LayerTypeABC


class FullText(LayerTypeABC):
    """A simple fulltext layer type"""

    class FullTextUnit(LayerTypeABC.UnitBase):
        text: str = Field(
            None,
            description="Text content of the fulltext unit",
            extra={"template": True},
        )

    @classmethod
    def get_description(cls) -> str:
        return "A simple fulltext data layer"

    @classmethod
    def get_unit_model(cls) -> type[FullTextUnit]:
        return cls.FullTextUnit
