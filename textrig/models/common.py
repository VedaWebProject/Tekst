from typing import Optional

# from bson import ObjectId
# from bson.errors import InvalidId
# from humps import camelize
# from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


# type alias for a flat dict of arbitrary metadata
Metadata = dict[str, str | int | bool | float]


# class TextRigBaseModel(BaseModel):
#     """Base class for all TextRig models"""

#     def dict(self, for_mongo: bool = False, **kwargs) -> dict:
#         """Overrides dict() in Basemodel to change some defaults"""
#         return super().dict(
#             exclude_unset=kwargs.pop("exclude_unset", True),
#             by_alias=kwargs.pop("by_alias", True),
#             **kwargs,
#         )

#     def json(self, **kwargs) -> str:
#         """Overrides json() in Basemodel to change some defaults"""
#         return super().json(
#             exclude_unset=kwargs.pop("exclude_unset", True),
#             by_alias=kwargs.pop("by_alias", True),
#             **kwargs,
#         )

#     def ensure_model_type(
#         self, target_model_type: "TextRigBaseModel"
#     ) -> "TextRigBaseModel":
#         """
#         Used to make sure that (especially subclass) model
#         instances pass validation for the target model. If it quacks like a duck...
#         """
#         if type(self) is not target_model_type:
#             return target_model_type(**self.dict())
#         return self

#     @classmethod
#     def field_names(cls, alias: bool = False):
#         return list(cls.schema(alias).get("properties").keys())

#     class Config:
#         alias_generator = camelize
#         allow_population_by_field_name = True


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
