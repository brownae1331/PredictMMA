from pydantic import BaseModel, constr, field_validator
from typing import Annotated

class UserRegister(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')]
    password: Annotated[str, constr(min_length=8)]

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')]
    password: Annotated[str, constr(min_length=8)]