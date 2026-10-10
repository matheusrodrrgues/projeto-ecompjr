import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class FornecedorBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=150)
    cnpj: str
    telefone: str = Field(min_length=8, max_length=20)
    email: EmailStr

    @field_validator("nome", "telefone", mode="before")
    @classmethod
    def limpar_texto(cls, valor: str) -> str:
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("cnpj", mode="before")
    @classmethod
    def normalizar_cnpj(cls, cnpj: str) -> str:
        apenas_numeros = re.sub(r"\D", "", cnpj)
        if len(apenas_numeros) != 14:
            raise ValueError("O CNPJ deve ter 14 dígitos.")
        return apenas_numeros


class FornecedorCriacao(FornecedorBase):
    pass


class FornecedorAtualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=2, max_length=150)
    cnpj: str | None = None
    telefone: str | None = Field(default=None, min_length=8, max_length=20)
    email: EmailStr | None = None

    @field_validator("nome", "telefone", mode="before")
    @classmethod
    def limpar_texto(cls, valor: str | None) -> str | None:
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("cnpj", mode="before")
    @classmethod
    def normalizar_cnpj(cls, cnpj: str | None) -> str | None:
        if cnpj is None:
            return None
        apenas_numeros = re.sub(r"\D", "", cnpj)
        if len(apenas_numeros) != 14:
            raise ValueError("O CNPJ deve ter 14 dígitos.")
        return apenas_numeros

    @model_validator(mode="after")
    def validar_alteracoes(self) -> "FornecedorAtualizacao":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Os campos informados não podem ser nulos.")
        return self


class FornecedorResposta(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
