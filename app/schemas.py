from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: str
    name: str
    email: str

    class Config():
        orm_mode = True


class Register(BaseModel):
    name: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None