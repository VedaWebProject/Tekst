from typing import Optional

from beanie import Document, PydanticObjectId

# from bson.errors import InvalidId
from humps import camelize
from pydantic import BaseModel
from pydantic.main import ModelMetaclass


# type alias for a flat dict of arbitrary metadata
Metadata = dict[str, str | int | bool | float]


class PyObjectId(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )


class _CRUDBase(BaseModel):
    """Base class for all TextRig pydantic models"""

    def dict(self, **kwargs) -> dict:
        """Overrides dict() in Basemodel to set custom defaults"""

        return super().dict(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    def json(self, **kwargs) -> str:
        """Overrides json() in Basemodel to change some defaults"""
        return super().json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    @classmethod
    def field_names(cls, alias: bool = False):
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


# class _FactoryMixin:
#     @classmethod
#     def from_(cls, obj: BaseModel, **dict_kwargs) -> BaseModel:
#         return cls(**obj.dict(**dict_kwargs))

#     def to_(self, model: type[BaseModel], **dict_kwargs) -> BaseModel:
#         return model(**self.dict(**dict_kwargs))


class _IDMixin(BaseModel):
    id: PyObjectId

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = str(kwargs.pop("_id"))
        super().__init__(**kwargs)


class DocumentBase(Document):
    """Base class for all TextRig ODM models"""

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    def dict(self, **kwargs) -> dict:
        from_base = super().dict(
            by_alias=kwargs.pop("by_alias", True),
            exclude_unset=kwargs.pop("exclude_unset", True),
            **kwargs,
        )
        # if "_id" in from_base:
        #     from_base["id"] = str(from_base.pop("_id"))
        return from_base

    def json(self, **kwargs) -> str:
        return super().json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    @classmethod
    def from_(cls, obj: _CRUDBase, **dict_kwargs) -> BaseModel:
        return cls(**obj.dict(**dict_kwargs))

    class Settings:
        pass

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class _AllOptional(ModelMetaclass):
    """
    Metaclass to render all fields of a pydantic model optional (on root level).
    This approach was taken from here:
    https://stackoverflow.com/a/67733889/7399631
    Alternative ones are discussed here:
    https://github.com/pydantic/pydantic/issues/1223#issuecomment-998160737
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__") and field not in ("id", "_id"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class CreateBase(_CRUDBase):
    pass


class ReadBase(_CRUDBase, _IDMixin):
    pass


class UpdateBase(_CRUDBase, metaclass=_AllOptional):
    pass


class ModelBase(BaseModel):

    _document_model: type[DocumentBase] = None
    _create_model: type[CreateBase] = None
    _read_model: type[ReadBase] = None
    _update_model: type[UpdateBase] = None

    @classmethod
    def _generate_model(
        cls, classname_suffix: str, base: type["ModelBase"]
    ) -> type["ModelBase"]:
        return type(
            f"{cls.__name__}{classname_suffix.capitalize()}",
            (cls, base),
            {"__module__": f"{cls.__module__}"},
        )

    @classmethod
    def get_document_model(
        cls, base: type["ModelBase"] = DocumentBase
    ) -> type[DocumentBase]:
        if not cls._document_model:
            cls._document_model = cls._generate_model("Document", base)
        return cls._document_model

    @classmethod
    def get_create_model(cls, base: type["ModelBase"] = CreateBase) -> type[CreateBase]:
        if not cls._create_model:
            cls._create_model = cls._generate_model("Create", base)
        return cls._create_model

    @classmethod
    def get_read_model(cls, base: type["ModelBase"] = ReadBase) -> type[ReadBase]:
        if not cls._read_model:
            cls._read_model = cls._generate_model("Read", base)
        return cls._read_model

    @classmethod
    def get_update_model(cls, base: type["ModelBase"] = UpdateBase) -> type[UpdateBase]:
        if not cls._update_model:
            cls._update_model = cls._generate_model("Update", base)
        return cls._update_model


# class RootModelBaseMixin:

#     _root_document_model: type[DocumentBase] = None
#     _root_update_model: type[UpdateBase] = None

#     @classmethod
#     def get_document_model(cls) -> type[DocumentBase]:
#         if cls == RootModelBaseMixin:
#             raise SystemExit(
#                 "This method is not meant to be called "
#                 "on RootModelBaseMixin class directly."
#             )
#         if cls.__name__.endswith("Base"):
#             if not cls._root_document_model:
#                 cls._root_document_model = cls._generate_model(
#                     "Document", DocumentBase
#                 )
#             return cls._root_document_model
#         if not cls._document_model:
#             if cls._root_document_model:
#                 cls._document_model = cls._generate_model(
#                     "Document", cls._root_document_model
#                 )
#             else:
#                 cls._document_model = cls._generate_model("Document", DocumentBase)
#         return cls._document_model

#     @classmethod
#     def get_update_model(cls) -> type[UpdateBase]:
#         if cls == RootModelBaseMixin:
#             raise SystemExit(
#                 "This method is not meant to be called "
#                 "on RootModelBaseMixin class directly."
#             )
#         if cls.__name__.endswith("Base"):
#             if not cls._root_update_model:
#                 cls._root_update_model = cls._generate_model("Update", UpdateBase)
#             return cls._root_update_model
#         if not cls._update_model:
#             if cls._root_update_model:
#                 cls._update_model = cls._generate_model(
#                     "Update", cls._root_update_model
#                 )
#             else:
#                 cls._update_model = cls._generate_model("Document", UpdateBase)
#         return cls._update_model
