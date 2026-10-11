"""Dados aceitos no cadastro e devolvidos na autenticação."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCriacao(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "nome": "Matheus Rodrigues",
                    "email": "matheus@example.com",
                    "senha": "senha-segura-123",
                }
            ]
        },
    )

    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome", mode="before")
    @classmethod
    def limpar_nome(cls, nome: str) -> str:
        """Remove espaços das pontas antes de validar o tamanho do nome."""
        return nome.strip() if isinstance(nome, str) else nome

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: EmailStr) -> str:
        """Salva o e-mail em minúsculas para a comparação de login e unicidade."""
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
