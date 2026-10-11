from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome", mode="before")
    @classmethod
    def limpar_nome(cls, nome: str) -> str:
        return nome.strip() if isinstance(nome, str) else nome

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: EmailStr) -> str:
        return str(email).lower()


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    criado_em: datetime


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
