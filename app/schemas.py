from pydantic import BaseModel


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
