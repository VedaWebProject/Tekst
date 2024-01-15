from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from tekst.models.common import ModelBase, PydanticObjectId
from tekst.models.node import NodeRead
from tekst.resources import AnyUnitRead


class NodeDefinition(ModelBase):
    label: Annotated[
        str,
        StringConstraints(min_length=1, max_length=256, strip_whitespace=True),
    ]
    nodes: list["NodeDefinition"] | None = None


class TextStructureImportData(ModelBase):
    model_config = ConfigDict(extra="allow")
    nodes: list[NodeDefinition] = []


class LocationData(ModelBase):
    node_path: list[NodeRead] = []
    units: Annotated[list[AnyUnitRead], Field(discriminator="resource_type")] = []


class ResourceImportData(ModelBase):
    resource_id: PydanticObjectId
    units: list[dict] = []


class ResourceDataImportResponse(ModelBase):
    updated: int
    created: int
