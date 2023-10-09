from typing import Annotated

from pydantic import ConfigDict, StringConstraints

from tekst.models.common import ModelBase


class NodeDefinition(ModelBase):
    label: Annotated[
        str,
        StringConstraints(min_length=1, max_length=256),
    ]
    children: list["NodeDefinition"] | None = None


class TextStructureDefinition(ModelBase):
    model_config = ConfigDict(extra="allow")
    structure: list[NodeDefinition] = []
