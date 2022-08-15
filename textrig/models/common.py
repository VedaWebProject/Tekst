from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class ObjectIdStr(ObjectId):
    """Wrapper model for MongoDB's object IDs"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DbModel(BaseModel):
    """Base model for all further TextRig data models"""

    id: ObjectIdStr = Field(default_factory=ObjectIdStr, alias="_id")

    class Config:
        json_encoders = {ObjectId: lambda x: str(x)}
