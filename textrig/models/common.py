import re
from typing import Optional

from beanie import Document, PydanticObjectId
from bson import ObjectId

# from bson.errors import InvalidId
# from humps import camelize
from pydantic import Field
from pydantic.main import ModelMetaclass


# type alias for a flat dict of arbitrary metadata
Metadata = dict[str, str | int | bool | float]


class DocumentBase(Document):
    """Base class for all TextRig DB models"""

    id: PydanticObjectId = Field(None, description="ID of this object")

    def dict(self, serialize_ids: bool = False, **kwargs) -> dict:
        """Overrides dict() in Basemodel to change some defaults"""

        parsed = super().dict(
            exclude_unset=kwargs.pop("exclude_unset", True),
            # by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )
        if serialize_ids:
            parsed = self._serialize_ids(parsed)
        return parsed

    def json(self, **kwargs) -> str:
        """Overrides json() in Basemodel to change some defaults"""
        return super().json(
            exclude_unset=kwargs.pop("exclude_unset", True),
            # by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

    async def insert(self, **kwargs):
        self.id = None  # reset ID for new document in case one is already set
        return await super().insert(**kwargs)

    def _serialize_ids(self, obj: "dict | list[dict]") -> dict:
        def encode_obj_ids(d: dict) -> dict:
            out = dict()
            for k, v in d.items():
                if not isinstance(k, str):
                    raise ValueError("Keys sould be strings")
                elif isinstance(v, dict):
                    out[k] = encode_obj_ids(v)
                elif re.match(r"^(id|_id|.*?Id|.*?_id)$", k):
                    if isinstance(v, ObjectId) or isinstance(v, PydanticObjectId):
                        out[k] = str(v)
                else:
                    out[k] = v
            return out

        if type(obj) is dict:
            return encode_obj_ids(obj)
        elif type(obj) is list:
            return [encode_obj_ids(o) for o in obj]
        else:
            raise TypeError(
                "The passed object must be of type "
                f"'dict' or 'list', got '{type(obj).__name__}'"
            )

    # def ensure_model_type(
    #     self, target_model_type: "TextRigBaseModel"
    # ) -> "TextRigBaseModel":
    #     """
    #     Used to make sure that (especially subclass) model
    #     instances pass validation for the target model. If it quacks like a duck...
    #     """
    #     if type(self) is not target_model_type:
    #         return target_model_type(**self.dict())
    #     return self

    @classmethod
    def field_names(cls, alias: bool = False):
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        json_encoders = {PydanticObjectId: str, ObjectId: str}

    #     alias_generator = camelize
    #     allow_population_by_field_name = True


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
