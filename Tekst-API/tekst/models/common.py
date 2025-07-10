from collections.abc import Iterable
from types import UnionType
from typing import (
    Any,
    Literal,
    Union,
    get_args,
    get_origin,
)  # noqa: UP035

from beanie import Document, PydanticObjectId
from beanie.odm.utils.encoder import Encoder
from humps import camelize, decamelize
from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    ValidationError,
    create_model,
)
from pydantic.aliases import PydanticUndefined
from pydantic.fields import FieldInfo

from tekst.types import (
    ExcludeFromModelVariants,
    SchemaOptionalNonNullable,
    SchemaOptionalNullable,
)


# MODEL BASE CLASSES


class ModelBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True,
        from_attributes=True,
    )

    def attr_by_path(self, path: str) -> Any:
        try:
            v = self
            for part in path.split("."):
                v = getattr(v, part, None)
                if v is None:  # pragma: no cover
                    return None
            return v
        except AttributeError:  # pragma: no cover
            return None

    @classmethod
    def model_from(cls, obj: BaseModel) -> BaseModel:
        return cls.model_validate(obj, from_attributes=True)

    @classmethod
    def _field_excluded_from_model_variant(
        cls,
        field_name: str,
        model_variant: Literal["create", "update"],
    ) -> bool:
        """
        Returns `True` if the field with the given name should be excluded from the
        model variant with the given name. This is the case if the field is annotated
        with `ExcludeFromModelVariants` with the given model variant set to `True`.
        """
        for meta in cls.model_fields[field_name].metadata:
            if isinstance(
                meta,
                ExcludeFromModelVariants,
            ) and getattr(
                meta,
                model_variant,
                False,
            ):
                return True
        return False


class NoAliasEncoder(Encoder):
    """
    A customized version of beanie.odm.utils.encoder.Encoder that ignores field aliases
    and just uses the actual field name. We have to do this to prevent nested models
    to appear in DB documents with their camelCased field aliases.
    """

    def _iter_model_items(self, obj: BaseModel) -> Iterable[tuple[str, Any]]:
        exclude, keep_nulls = self.exclude, self.keep_nulls
        for key, value in obj.__iter__():
            if key not in exclude and (value is not None or keep_nulls):
                # this is where we use "key" directly, without considering aliases
                yield key, value


_no_alias_encoder = NoAliasEncoder(to_db=True, keep_nulls=False).encode


class DocumentBase(Document):
    """Base model for all Tekst ODMs"""

    class Settings:
        # this might be costly, but as we don't have transactions or anything like that
        # we must do all we can to make sure a bug doesn't break the data
        validate_on_save = True
        keep_nulls = False
        bson_encoders = {
            # see docstring of NoAliasEncoder for rationale!
            BaseModel: _no_alias_encoder,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **decamelize(kwargs))

    async def insert(self, **kwargs):
        self.id = None  # prevent creating documents with a pre-existing ID
        return await super().insert(**kwargs)

    async def apply_updates(
        self,
        updates_model: ModelBase,
        *,
        replace: bool = True,
    ):
        """
        Custom method to apply updates to the document, excluding any fields that are
        - not set in `updates_model`
        - equal to the default value of the respective field in `updates_model`
        """
        for field in updates_model.model_fields_set:
            # we have to always preserve `resource_type`, so skip updating it
            if field == "resource_type":
                continue
            # make sure we ignore None values that sneaked in because
            # the update models allow them but the original model does not
            if getattr(
                updates_model, field
            ) is None and not self._validate_against_field(field, None):
                continue
            # set attribute
            setattr(self, field, getattr(updates_model, field))

        if replace:
            return await self.replace()
        else:
            return self

    @classmethod
    def _validate_against_field(
        cls,
        field_name: str,
        value: Any,
    ) -> bool:
        field_adapter = TypeAdapter(cls.model_fields[field_name].annotation)
        try:
            field_adapter.validate_python(value)
            return True
        except ValidationError:
            return False


class CreateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for name, field in list(cls.model_fields.items()):
            if cls._field_excluded_from_model_variant(name, "create"):
                field.default = PydanticUndefined
                del cls.model_fields[name]

        cls.model_rebuild(force=True)


class ReadBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: PydanticObjectId


class UpdateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for name, field in list(cls.model_fields.items()):
            if cls._field_excluded_from_model_variant(name, "update"):
                del cls.model_fields[name]

        cls.model_rebuild(force=True)


# MODEL FACTORY MIXIN


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
    def document_model(cls, bases: type | tuple[type] = DocumentBase) -> type:
        if not cls._document_model or not cls._is_origin_cls("_document_model"):
            cls._document_model = create_model(
                f"{cls.__name__}Document",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._document_model

    @classmethod
    def create_model(cls, bases: type | tuple[type] = CreateBase) -> type[ModelBase]:
        if not cls._create_model or not cls._is_origin_cls("_create_model"):
            cls._create_model = create_model(
                f"{cls.__name__}Create",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._create_model

    @classmethod
    def read_model(cls, bases: type | tuple[type] = ReadBase) -> type[ReadBase]:
        if not cls._read_model or not cls._is_origin_cls("_read_model"):
            cls._read_model = create_model(
                f"{cls.__name__}Read",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
            )
        return cls._read_model

    @classmethod
    def update_model(cls, bases: type | tuple[type] = UpdateBase) -> type[ModelBase]:
        if not cls._update_model or not cls._is_origin_cls("_update_model"):
            field_overrides = {}
            for name, field in cls.model_fields.items():
                if name.endswith("_type"):
                    continue  # don't make fields optional that end on "_type"
                type_annos = (
                    (field.annotation,)
                    if get_origin(field.annotation) not in (Union, UnionType)
                    else get_args(field.annotation)
                )
                extra_field_infos = []
                if not cls._validate_against_field(name, None):
                    # None isn't a valid value for this field yet, so we add it to types
                    type_annos += (type(None),)
                    # mark that this prop wasn't originally nullable
                    extra_field_infos.append(SchemaOptionalNonNullable)
                else:
                    # mark that this prop was originally nullable
                    extra_field_infos.append(SchemaOptionalNullable)
                # merge with original field info
                fi = FieldInfo.merge_field_infos(
                    field,
                    *extra_field_infos,
                    # set the type annotation to a union of the composed types
                    annotation=Union[type_annos],  # noqa: UP007
                    # we always default to None on these update model fields
                    default=None,
                )
                # add to field overrides
                field_overrides[name] = (fi.annotation, fi)
            cls._update_model = create_model(
                f"{cls.__name__}Update",
                __base__=(cls, *cls._to_bases_tuple(bases)),
                __module__=cls.__module__,
                **field_overrides,
            )
        return cls._update_model

    @classmethod
    def _validate_against_field(
        cls,
        field_name: str,
        value: Any,
    ) -> bool:
        field_adapter = TypeAdapter(cls.model_fields[field_name].annotation)
        try:
            field_adapter.validate_python(value)
            return True
        except ValidationError:
            return False
