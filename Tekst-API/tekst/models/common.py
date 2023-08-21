from datetime import datetime
from typing import Any, Dict, Literal

from beanie import (
    Document,
    PydanticObjectId,
)
from humps import camelize, decamelize
from pydantic import BaseModel, ConfigDict, create_model


# type alias for a flat dict of arbitrary metadata
Metadata = Dict[str, str]

# type alias for available locale identifiers
Locale = Literal["deDE", "enUS"]


class ModelTransformerMixin:
    @classmethod
    def model_from(cls, obj: BaseModel) -> BaseModel:
        return cls.model_validate(obj, from_attributes=True)


class ModelBase(ModelTransformerMixin, BaseModel):
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True, from_attributes=True)

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Overrides model_dump() in Basemodel to set some custom defaults"""
        data = super().model_dump(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )
        return data

    def model_dump_json(self, **kwargs) -> str:
        """Overrides model_dump_json() in Basemodel to set some custom defaults"""
        return super().model_dump_json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )


class DocumentBase(ModelTransformerMixin, Document):
    """Base model for all Tekst ODM models"""

    # model_config = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **decamelize(kwargs))

    def model_dump(
        self, rename_id: bool = True, camelize_keys: bool = True, **kwargs
    ) -> dict[str, Any]:
        """Overrides model_dump() in Basemodel to set some custom defaults"""
        data = super().model_dump(
            exclude_unset=kwargs.pop("exclude_unset", True),
            **kwargs,
        )
        if rename_id and "_id" in data:
            data["id"] = data.pop("_id")
        return camelize(data) if camelize_keys else data

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
        return await self.set(decamelize(updates), **kwargs)

    class Settings:
        pass


class ReadBase:
    id: PydanticObjectId


class ModelFactoryMixin:
    _document_model: type[DocumentBase] = None
    _create_model: type[ModelBase] = None
    _read_model: type[ReadBase] = None
    _update_model: type[ModelBase] = None

    @classmethod
    def _is_origin_cls(cls, attr: str) -> bool:
        for clazz in cls.mro():
            if attr in vars(clazz):
                return clazz == cls
        raise AttributeError(f"Attribute '{attr}' not found in class '{cls.__name__}'")

    @classmethod
    def _to_bases_tuple(cls, bases: type | tuple[type]):
        return (bases,) if type(bases) is not tuple else bases

    @classmethod
    def get_document_model(cls, bases: type | tuple[type] = (DocumentBase,)) -> type:
        if not cls._document_model or not cls._is_origin_cls("_document_model"):
            cls._document_model = type(
                f"{cls.__name__}Document",
                (cls, *cls._to_bases_tuple(bases)),
                {"__module__": f"{cls.__module__}"},
            )
        return cls._document_model

    @classmethod
    def get_create_model(cls) -> type[ModelBase]:
        if not cls._create_model or not cls._is_origin_cls("_create_model"):
            cls._create_model = cls
        return cls._create_model

    @classmethod
    def get_read_model(cls, bases: type | tuple[type] = (ReadBase,)) -> type[ReadBase]:
        if not cls._read_model or not cls._is_origin_cls("_read_model"):
            cls._read_model = type(
                f"{cls.__name__}Read",
                (cls, *cls._to_bases_tuple(bases)),
                {"__module__": f"{cls.__module__}"},
            )
        return cls._read_model

    @classmethod
    def get_update_model(cls, bases: type | tuple[type] = ()) -> type[ModelBase]:
        if not cls._update_model or not cls._is_origin_cls("_update_model"):
            fields = {}
            for k, v in cls.model_fields.items():
                fields[k] = (v.annotation, None)
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__name__,
                **fields,
            )
        return cls._update_model


class LayerConfigBase(ModelBase):
    pass
