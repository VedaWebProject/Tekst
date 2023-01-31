from typing import Optional

from beanie import Document

# from pydantic import Field
from humps import camelize
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


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


class _FactoryMixin:
    @classmethod
    def from_(cls, obj: BaseModel, **dict_kwargs) -> BaseModel:
        return cls(**obj.dict(**dict_kwargs))

    def to_(self, model: type[BaseModel], **dict_kwargs) -> BaseModel:
        return model(**self.dict(**dict_kwargs))


class _IDMixin(BaseModel):
    id: str

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = str(kwargs.pop("_id"))
        super().__init__(**kwargs)


class _DocumentBase(Document, _FactoryMixin):
    """Base class for all TextRig DB document models"""

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    def dict(self, **kwargs) -> dict:
        from_base = super().dict(
            by_alias=kwargs.pop("by_alias", True),
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


class _CreateBase(_CRUDBase, _FactoryMixin):
    pass


class _ReadBase(_CRUDBase, _IDMixin, _FactoryMixin):
    pass


class _UpdateBase(_CRUDBase, _IDMixin, _FactoryMixin, metaclass=_AllOptional):
    pass


class ModelBase(BaseModel):

    __document_model: type[_DocumentBase] = None
    __create_model: type[_CreateBase] = None
    __read_model: type[_ReadBase] = None
    __update_model: type[_UpdateBase] = None

    @classmethod
    def __generate_model(cls, suffix: str, base: type) -> type["ModelBase"]:
        return type(
            f"{cls.__name__}{suffix.capitalize()}",
            (cls, base),
            {"__module__": f"{cls.__module__}"},
        )

    @classmethod
    def get_document_model(cls) -> type[_DocumentBase]:
        if not cls.__document_model:
            # generate document model
            cls.__document_model = cls.__generate_model("Document", _DocumentBase)
        return cls.__document_model

    @classmethod
    def get_create_model(cls) -> type[_CRUDBase]:
        if not cls.__create_model:
            cls.__create_model = cls.__generate_model("Create", _CreateBase)
        return cls.__create_model

    @classmethod
    def get_read_model(cls) -> type[_CRUDBase]:
        if not cls.__read_model:
            cls.__read_model = cls.__generate_model("Read", _ReadBase)
        return cls.__read_model

    @classmethod
    def get_update_model(cls) -> type[_CRUDBase]:
        if not cls.__update_model:
            cls.__update_model = cls.__generate_model("Update", _UpdateBase)
        return cls.__update_model


class _FooBase(ModelBase):
    foo_bar: str = Field("baz", min_length=1, max_length=64, description="Fooo Baaaaar")

    class Settings:
        name = "foos"


FooDocument = _FooBase.get_document_model()
FooCreate = _FooBase.get_create_model()
FooRead = _FooBase.get_read_model()
FooUpdate = _FooBase.get_update_model()
