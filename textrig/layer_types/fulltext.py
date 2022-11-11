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

    class FullTextUnitRead(FullTextUnit, LayerTypeABC.UnitReadBase):
        ...

    class FullTextUnitUpdate(FullTextUnit, LayerTypeABC.UnitUpdateBase):
        ...

    @classmethod
    def get_description(cls) -> str:
        return "A simple fulltext data layer"

    @classmethod
    def get_unit_model(cls) -> type[FullTextUnit]:
        return cls.FullTextUnit

    @classmethod
    def get_unit_read_model(cls) -> type[FullTextUnitRead]:
        return cls.FullTextUnitRead

    @classmethod
    def get_unit_update_model(cls) -> type[FullTextUnitUpdate]:
        return cls.FullTextUnitUpdate
