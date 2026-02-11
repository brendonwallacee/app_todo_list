from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class EmpresaSchema(BaseModel):
    id: int
    razao_social: str
    cnpj: str


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
