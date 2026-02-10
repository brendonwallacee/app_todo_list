from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Empresa(BaseModel):
    id: int
    razao_social: str
    cnpj: str
