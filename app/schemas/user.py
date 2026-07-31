from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Password = Annotated[str, StringConstraints(min_length=6, max_length=128)]


class UserCreate(BaseModel):
    name: Name
    email: EmailStr
    password: Password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
