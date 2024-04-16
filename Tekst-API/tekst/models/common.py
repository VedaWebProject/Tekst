from typing import (  # noqa: UP035
    Annotated,
    Literal,
    TypeVar,
    get_args,
)

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
    conlist,
    create_model,
)
from typing_extensions import TypeAliasType, TypedDict


# class for one arbitrary metadate
class Metadate(TypedDict):
    key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=128,
            strip_whitespace=True,
        ),
    ]


# type alias for collection of arbitrary metadata
Metadata = Annotated[
    list[Metadate],
    Field(
        description="Arbitrary metadata",
        min_length=0,
        max_length=64,
    ),
]


# type alias for available locale/language setting identifiers
_platform_locales = ("deDE", "enUS")
LocaleKey = TypeAliasType("LocaleKey", Literal[_platform_locales])
TranslationLocaleKey = TypeAliasType(
    "TranslationLocaleKey", Literal[_platform_locales + ("*",)]
)

# Pydantic HttpUrl with string serialization
CustomHttpUrl = Annotated[
    HttpUrl,
    PlainSerializer(
        lambda url: str(url),
        return_type=str,
        when_used="always",
    ),
]


# translations
class TranslationBase(TypedDict):
    locale: TranslationLocaleKey


T = TypeVar("T", bound=TranslationBase)
Translations = conlist(
    T,
    max_length=len(get_args(TranslationLocaleKey.__value__)),
)


class ModelTransformerMixin:
    @classmethod
    def model_from(cls, obj: BaseModel) -> BaseModel:
        return cls.model_validate(obj, from_attributes=True)


class ModelBase(ModelTransformerMixin, BaseModel):
    model_config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True,
        from_attributes=True,
    )


class DocumentBase(ModelTransformerMixin, Document):
    """Base model for all Tekst ODM models"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **decamelize(kwargs))

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    async def apply_updates(
        self,
        updates_model: BaseModel,
        *,
        exclude: set[int] | set[str] | None = None,
        **kwargs,
    ):
        """
        Custom method to apply updates to the document. It does a few things of which
        some are tricky to do with pure Pydantic or Beanie:
        1. only applies set fields
        2. excludes fields that are passed in `exclude`
        3. (most importantly) avoids serialization of the values (e.g. ObjectId -> str)
        """
        for field in updates_model.model_fields_set:
            if not exclude or field not in exclude:
                setattr(self, field, getattr(updates_model, field))
        return await self.replace()

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
        raise AttributeError(
            f"Attribute '{attr}' not found in class '{cls.__name__}'"
        )  # pragma: no cover

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
                    fields[k] = (
                        (Annotated[(v.annotation | None, *v.metadata)], None)
                        if v.metadata
                        else (v.annotation | None, None)
                    )
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
                **fields,
            )
        return cls._update_model
