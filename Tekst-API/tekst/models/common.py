from collections.abc import Iterable
from datetime import UTC, datetime
from typing import (
    Annotated,
    Any,
    Literal,
    Self,
)
from unicodedata import normalize

from beanie import Document, PydanticObjectId
from beanie.odm.utils.encoder import Encoder
from humps import camelize, decamelize
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    create_model,
)
from pydantic.aliases import PydanticUndefined

from tekst.config import get_config
from tekst.types import (
    ExcludeFromModelVariants,
)


# MODEL BASE CLASSES


class ModelBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=camelize,
        validate_by_name=True,
        validate_by_alias=True,
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
    def model_from(cls, obj: BaseModel) -> Self:
        return cls.model_validate(obj, from_attributes=True)

    @classmethod
    def validate_against_field(
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


class NoAliasEncoder(Encoder):
    """
    A customized version of beanie.odm.utils.encoder.Encoder that ignores field aliases
    and just uses the actual field name. We have to do this to prevent nested models
    to appear in DB documents with their camelCased field aliases.
    """

    def _iter_model_items(self, obj: BaseModel) -> Iterable[tuple[str, Any]]:
        for key, value in obj.__iter__():
            if key not in self.exclude and (value is not None or self.keep_nulls):
                # this is where we use "key" directly, without considering aliases
                yield key, value


_no_alias_encoder = NoAliasEncoder(to_db=True, keep_nulls=False).encode
_unicode_nf = get_config().db.unicode_nf


def _apply_unicode_nf(str_v):
    if _unicode_nf is not None:
        return normalize(_unicode_nf, str_v)
    else:  # pragma: no cover
        return str_v


class DocumentBase(Document):
    """Base model for all Tekst ODMs"""

    class Settings:
        # this might be costly, but as we don't have transactions or anything like that
        # we must do all we can to make sure a bug doesn't break the data
        validate_on_save = True
        keep_nulls = False
        bson_encoders = {
            BaseModel: _no_alias_encoder,  # see docstring of NoAliasEncoder
            str: _apply_unicode_nf,
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
        insert: bool = False,
        update_created_at: bool = False,
    ) -> "DocumentBase":
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
            if getattr(updates_model, field) is None and not type(
                self
            ).validate_against_field(field, None):
                continue  # pragma: no cover
            # set attribute
            setattr(self, field, getattr(updates_model, field))

        if update_created_at:
            setattr(self, "created_at", datetime.now(UTC))

        if insert:
            return await self.save()  # same as self.insert()
        else:
            return await self.replace()  # raises exception if document does not exist


def _field_excluded_from_model_variant(
    model_type: type[BaseModel],
    field_name: str,
    model_variant: Literal["create", "update"],
) -> bool:
    """
    Returns `True` if the field with the given name should be excluded from the
    model variant with the given name. This is the case if the field is annotated
    with `ExcludeFromModelVariants` with the given model variant set to `True`.
    """
    for meta in model_type.model_fields[field_name].metadata:
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


def _apply_field_exclusions(
    model_type: type[BaseModel],
    model_variant: Literal["create", "update"],
) -> None:
    for field_name, field in list(model_type.model_fields.items()):
        if _field_excluded_from_model_variant(model_type, field_name, model_variant):
            field.default = PydanticUndefined
            del model_type.model_fields[field_name]
    model_type.model_rebuild(force=True)


def make_update_model[ModelTypeT: type[ModelBase]](
    model_cls: ModelTypeT,
    *,
    extra_bases: tuple[type] | None = None,
) -> ModelTypeT:
    field_overrides = {}

    for f_name, f_info in model_cls.model_fields.items():
        # skip fields that end with _type, e.g. `resource_type`
        if f_name.endswith("_type"):
            continue

        # use the FieldInfo data as dict because mutating FieldInfo instances
        # is unsupported by pydantic and can lead to unexpected behavior
        f_dict: dict[str, Any] = f_info.asdict()

        # remove `default_factory` entries from field infos
        if "attributes" in f_dict and "default_factory" in f_dict["attributes"]:
            del f_dict["attributes"]["default_factory"]

        # set SchemaOptionalNullable or SchemaOptionalNonNullable as metadata
        if not f_dict["attributes"].get("json_schema_extra"):
            f_dict["attributes"]["json_schema_extra"] = {}
        if (
            f_dict["attributes"]["json_schema_extra"].get("optionalNullable")
            is not False
        ):
            f_dict["attributes"]["json_schema_extra"]["optionalNullable"] = (
                model_cls.validate_against_field(f_name, None)
            )

        field_overrides[f_name] = (
            Annotated[
                f_info.annotation,
                *f_dict["metadata"],
                # *nullable_anno,
                Field(**f_dict["attributes"]),
            ],
            None,
        )

    return create_model(
        f"{model_cls.__name__}Update",
        __base__=(model_cls, UpdateBase, *(extra_bases or [])),
        __module__=model_cls.__module__,
        **field_overrides,
    )  # ty:ignore[no-matching-overload] # no idea what ty is complaining about here


class CreateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        _apply_field_exclusions(cls, "create")


class ReadBase(BaseModel):
    model_config = ConfigDict(extra="allow")  # TODO: do we need this?
    id: PydanticObjectId


class UpdateBase(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        _apply_field_exclusions(cls, "update")
