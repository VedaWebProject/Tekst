from datetime import datetime
from typing import Annotated, Any, Literal, Optional  # noqa: UP035

from beanie import (
    Document,
    PydanticObjectId,
)
from humps import camelize, decamelize
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PlainSerializer,
    StringConstraints,
    create_model,
)
from typing_extensions import TypedDict


# class for one arbitrary metadate
class Metadate(TypedDict):
    key: Annotated[str, StringConstraints(min_length=1, max_length=16)]
    value: Annotated[str, StringConstraints(min_length=1, max_length=128)]


# type alias for collection of arbitrary metadata
Metadata = Annotated[
    list[Metadate] | None,
    Field(description="Arbitrary metadata", min_length=0, max_length=64),
]


# type alias for available locale identifiers
Locale = Literal["deDE", "enUS"]

# Pydantic HttpUrl with string serialization
CustomHttpUrl = Annotated[
    HttpUrl, PlainSerializer(lambda url: str(url), return_type=str, when_used="always")
]


class ModelTransformerMixin:
    @classmethod
    def model_from(cls, obj: BaseModel) -> BaseModel:
        return cls.model_validate(obj, from_attributes=True)


class ModelBase(ModelTransformerMixin, BaseModel):
    model_config = ConfigDict(
        alias_generator=camelize, populate_by_name=True, from_attributes=True
    )


class DocumentBase(ModelTransformerMixin, Document):
    """Base model for all Tekst ODM models"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **decamelize(kwargs))

    def model_dump(self, camelize_keys: bool = False, **kwargs) -> dict[str, Any]:
        if camelize_keys:
            return camelize(super().model_dump(**kwargs))
        return super().model_dump(**kwargs)

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    async def apply(self, updates: dict, **kwargs):
        updates["modified_at"] = datetime.utcnow()
        return await self.set(decamelize(updates), **kwargs)

    class Settings:
        pass


class ReadBase:
    model_config = ConfigDict(extra="allow")
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
    def document_model(cls, bases: type | tuple[type] = (DocumentBase,)) -> type:
        if not cls._document_model or not cls._is_origin_cls("_document_model"):
            cls._document_model = create_model(
                f"{cls.__name__}Document",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._document_model

    @classmethod
    def create_model(cls) -> type[ModelBase]:
        if not cls._create_model or not cls._is_origin_cls("_create_model"):
            cls._create_model = create_model(
                f"{cls.__name__}Create",
                __base__=cls,
                __module__=cls.__module__,
            )
        return cls._create_model

    @classmethod
    def read_model(cls, bases: type | tuple[type] = (ReadBase,)) -> type[ReadBase]:
        if not cls._read_model or not cls._is_origin_cls("_read_model"):
            cls._read_model = create_model(
                f"{cls.__name__}Read",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._read_model

    @classmethod
    def update_model(cls, bases: type | tuple[type] = ()) -> type[ModelBase]:
        if not cls._update_model or not cls._is_origin_cls("_update_model"):
            fields = {}
            for k, v in cls.model_fields.items():
                if not str(k).endswith("_type") and v.is_required():
                    fields[k] = (Optional[v.annotation], None)  # noqa: UP007
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
                **fields,
            )
        return cls._update_model


class LayerConfigBase(ModelBase):
    pass
