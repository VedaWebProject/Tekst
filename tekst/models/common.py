from typing import Optional

from beanie import Document, PydanticObjectId
from humps import camelize
from pydantic import BaseModel
from pydantic.main import ModelMetaclass


# type alias for a flat dict of arbitrary metadata
Metadata = dict[str, str]


class PyObjectId(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )


class ModelBase(BaseModel):
    def dict(self, rename_id: bool = True, **kwargs) -> dict:
        """Overrides dict() in Basemodel to set some custom defaults"""
        data = super().dict(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )
        if rename_id and "_id" in data:
            data["id"] = data.pop("_id")
        return data

    def json(self, **kwargs) -> str:
        """Overrides json() in Basemodel to set some custom defaults"""
        return super().json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class _IDMixin(BaseModel):
    id: PyObjectId

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = str(kwargs.pop("_id"))
        super().__init__(**kwargs)


class DocumentBase(Document):
    """Base class for all Tekst ODM models"""

    def restricted_fields(self, user_id: str = None) -> dict:
        """
        This may or may not be overridden to define access-restricted fields
        that should be excluded from .dict() and .json() calls based on
        the given user ID trying to access data.
        IMPORTANT: We have to use snake_cased field names in the output dict!
        Not the camelCased aliases!
        """
        return None

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    class Settings:
        pass


class AllOptionalMeta(ModelMetaclass):
    """
    Metaclass to render all fields of a pydantic model optional (on root level).
    This approach was taken from here:
    https://stackoverflow.com/a/67733889/7399631
    Alternative ones are discussed here:
    https://github.com/pydantic/pydantic/issues/1223#issuecomment-998160737
    """

    def __new__(cls, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__") and field not in ("id", "_id"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class CreateBase(ModelBase):
    pass


class ReadBase(ModelBase, _IDMixin):
    pass


class UpdateBase(ModelBase, metaclass=AllOptionalMeta):
    pass


class ModelFactory:
    _document_model: type[DocumentBase] = None
    _create_model: type[CreateBase] = None
    _read_model: type[ReadBase] = None
    _update_model: type[UpdateBase] = None

    @classmethod
    def _generate_model(cls, classname_suffix: str, base: type) -> type["ModelFactory"]:
        return type(
            f"{cls.__name__}{classname_suffix.capitalize()}",
            (cls, base),
            {"__module__": f"{cls.__module__}"},
        )

    @classmethod
    def get_document_model(cls, base: type[DocumentBase] = DocumentBase) -> type:
        if not cls._document_model:
            cls._document_model = cls._generate_model("Document", base)
        return cls._document_model

    @classmethod
    def get_create_model(cls, base: type[CreateBase] = CreateBase) -> type[CreateBase]:
        if not cls._create_model:
            cls._create_model = cls._generate_model("Create", base)
        return cls._create_model

    @classmethod
    def get_read_model(cls, base: type[ReadBase] = ReadBase) -> type[ReadBase]:
        if not cls._read_model:
            cls._read_model = cls._generate_model("Read", base)
        return cls._read_model

    @classmethod
    def get_update_model(cls, base: type[UpdateBase] = UpdateBase) -> type[UpdateBase]:
        if not cls._update_model:
            cls._update_model = cls._generate_model("Update", base)
        return cls._update_model


class LayerConfigBase(ModelBase):
    pass
