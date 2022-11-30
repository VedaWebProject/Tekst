from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from humps import camelize
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


# type alias for a flat dict of arbitrary metadata
Metadata = dict[str, str | int | bool | float]


class DocumentId(ObjectId):
    """A project specific wrapper for MongoDB's bson.ObjectId"""

    def __repr__(self):
        return f"DocId('{str(self)}')"

    def __eq__(self, other):
        if not isinstance(other, (DocumentId, ObjectId, str)):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> "DocumentId":
        if type(v) is DocumentId:
            return v

        try:
            return DocumentId(str(v))
        except InvalidId:
            raise ValueError("Not a valid DocumentId")

    @classmethod
    def __modify_schema__(cls, field_schema) -> None:
        field_schema.update(type="string")


class TextRigBaseModel(BaseModel):
    """Base class for all TextRig models"""

    def __init__(self, **kwargs):
        """Converts "_id" to "id" """
        if "_id" in kwargs and kwargs["_id"]:
            kwargs["id"] = kwargs.pop("_id")
        super().__init__(**kwargs)

    def dict(self, for_mongo: bool = False, **kwargs) -> dict:
        """Overrides dict() in Basemodel to handle "_id" and change some defaults"""
        parsed = super().dict(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )
        if for_mongo and "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")
        if not for_mongo:
            for key in parsed:
                if type(parsed[key]) == DocumentId:
                    parsed[key] = str(parsed[key])
        return parsed

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
        json_encoders = {
            ObjectId: lambda oid: str(oid),
            DocumentId: lambda poid: str(poid),  # is this necessary?
        }


class DbDocument(BaseModel):
    """Schema mixin for objects in the database (which have an ID)"""

    id: DocumentId = Field(...)

    class Config:
        arbitrary_types_allowed = True
        # allow_population_by_field_name = True  # only needed for aliased fields


class AllOptional(ModelMetaclass):
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
