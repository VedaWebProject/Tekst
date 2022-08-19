from pydantic import EmailStr
from textrig.models.common import AllOptional, BaseModel, IDModelMixin


class UserCreate(BaseModel):

    username: str
    email: EmailStr


class UserUpdate(UserCreate, metaclass=AllOptional):
    pass


class User(UserCreate, IDModelMixin):
    pass
