from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Register(BaseModel):
    name: str
    email: str
    password: str
