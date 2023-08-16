from datetime import datetime
from typing import Dict, Literal

from beanie import (
    Document,
    PydanticObjectId,
)
from humps import camelize
from pydantic import BaseModel, ConfigDict, Field, create_model


# type alias for a flat dict of arbitrary metadata
Metadata = Dict[str, str]

# type alias for available locale identifiers
Locale = Literal["deDE", "enUS"]


class ModelBase(BaseModel):
    def model_dump(self, rename_id: bool = True, **kwargs) -> dict:
        """Overrides model_dump() in Basemodel to set some custom defaults"""
        data = super().model_dump(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )
        if rename_id and "_id" in data:
            data["id"] = data.pop("_id")
        return data

    def model_dump_json(self, **kwargs) -> str:
        """Overrides model_dump_json() in Basemodel to set some custom defaults"""
        return super().model_dump_json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)


class DocumentBase(Document):
    """Base model for all Tekst ODM models"""

    def restricted_fields(self, user_id: str = None) -> dict:
        """
        This may or may not be overridden to define access-restricted fields
        that should be excluded from .model_dump() and .model_dump_json() calls based on
        the given user ID trying to access data.
        IMPORTANT: We have to use snake_cased field names in the output dict!
        Not the camelCased aliases!
        """
        return None

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    async def apply(self, updates: dict, **kwargs):
        updates["modifiedAt"] = datetime.utcnow()
        return await self.set(updates, **kwargs)

    class Settings:
        pass


class ReadBase():
    id: PydanticObjectId

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = str(kwargs.pop("_id", kwargs["id"]))
        super().__init__(**kwargs)


class ModelFactory:
    _document_model: type[DocumentBase] = None
    _create_model: type[ModelBase] = None
    _read_model: type[ReadBase] = None
    _update_model: type[ModelBase] = None

    @classmethod
    def get_document_model(cls, base: type[DocumentBase] = DocumentBase) -> type:
        if not cls._document_model:
            cls._document_model = type(
                f"{cls.__name__}Document",
                (base, cls),
                {"__module__": f"{cls.__module__}"},
            )
        return cls._document_model

    @classmethod
    def get_create_model(cls) -> type[ModelBase]:
        return cls

    @classmethod
    def get_read_model(cls) -> type[ReadBase]:
        if not cls._read_model:
            cls._read_model = type(
                f"{cls.__name__}Read",
                (cls, ReadBase),
                {"__module__": f"{cls.__module__}"},
            )
        return cls._read_model

    @classmethod
    def get_update_model(
        cls, additional_bases: type | tuple[type] = ()
    ) -> type[ModelBase]:
        if not cls._update_model:
            fields = {}
            for k, v in cls.model_fields.items():
                fields[k] = (v.annotation, None)
            additional_bases = (
                (additional_bases,)
                if type(additional_bases) is not tuple
                else additional_bases
            )
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *additional_bases),
                __module__=cls.__name__,
                **fields,
            )
        return cls._update_model


class LayerConfigBase(ModelBase):
    pass
