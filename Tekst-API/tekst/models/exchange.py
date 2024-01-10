from typing import Annotated

from pydantic import ConfigDict, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.node import NodeRead
from tekst.resource_types import AnyUnitReadBody


class NodeDefinition(ModelBase):
    label: Annotated[
        str,
        StringConstraints(min_length=1, max_length=256, strip_whitespace=True),
    ]
    nodes: list["NodeDefinition"] | None = None


class TextStructureDefinition(ModelBase):
    model_config = ConfigDict(extra="allow")
    nodes: list[NodeDefinition] = []


class LocationData(ModelBase):
    node_path: list[NodeRead] = []
    units: list[AnyUnitReadBody] = []
