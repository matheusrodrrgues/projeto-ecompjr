"""Validação e normalização dos dados de fornecedores."""

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
        """Remove espaços extras antes das validações de tamanho dos campos."""
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("cnpj", mode="before")
    @classmethod
    def normalizar_cnpj(cls, cnpj: str) -> str:
        """Aceita CNPJ com máscara e guarda somente seus 14 números."""
        apenas_numeros = re.sub(r"\D", "", cnpj)
        if len(apenas_numeros) != 14:
            raise ValueError("O CNPJ deve ter 14 dígitos.")
        return apenas_numeros


class FornecedorCriacao(FornecedorBase):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "nome": "Atacado Central",
                    "cnpj": "12.345.678/0001-90",
                    "telefone": "75999999999",
                    "email": "contato@atacadocentral.com.br",
                }
            ]
        },
    )


class FornecedorAtualizacao(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [{"telefone": "7533334444", "email": "novo@atacadocentral.com.br"}]
        },
    )

    nome: str | None = Field(default=None, min_length=2, max_length=150)
    cnpj: str | None = None
    telefone: str | None = Field(default=None, min_length=8, max_length=20)
    email: EmailStr | None = None

    @field_validator("nome", "telefone", mode="before")
    @classmethod
    def limpar_texto(cls, valor: str | None) -> str | None:
        """Limpa somente os textos presentes no corpo da atualização."""
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("cnpj", mode="before")
    @classmethod
    def normalizar_cnpj(cls, cnpj: str | None) -> str | None:
        """Aplica ao novo CNPJ a mesma normalização usada no cadastro."""
        if cnpj is None:
            return None
        apenas_numeros = re.sub(r"\D", "", cnpj)
        if len(apenas_numeros) != 14:
            raise ValueError("O CNPJ deve ter 14 dígitos.")
        return apenas_numeros

    @model_validator(mode="after")
    def validar_alteracoes(self) -> "FornecedorAtualizacao":
        """Exige ao menos uma alteração e rejeita campos enviados como nulos."""
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Os campos informados não podem ser nulos.")
        return self


class FornecedorResposta(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
