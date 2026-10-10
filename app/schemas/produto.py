from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProdutoBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=150)
    sku: str = Field(min_length=2, max_length=50)
    preco_custo: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    estoque_minimo: int = Field(default=0, ge=0)
    categoria_id: int = Field(gt=0)
    fornecedor_id: int = Field(gt=0)

    @field_validator("nome", "sku")
    @classmethod
    def limpar_texto(cls, valor: str) -> str:
        return valor.strip()

    @field_validator("sku")
    @classmethod
    def padronizar_sku(cls, sku: str) -> str:
        return sku.upper()


class ProdutoCriacao(ProdutoBase):
    pass


class ProdutoAtualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=2, max_length=150)
    sku: str | None = Field(default=None, min_length=2, max_length=50)
    preco_custo: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    estoque_minimo: int | None = Field(default=None, ge=0)
    categoria_id: int | None = Field(default=None, gt=0)
    fornecedor_id: int | None = Field(default=None, gt=0)

    @field_validator("nome", "sku")
    @classmethod
    def limpar_texto(cls, valor: str | None) -> str | None:
        return valor.strip() if valor is not None else None

    @field_validator("sku")
    @classmethod
    def padronizar_sku(cls, sku: str | None) -> str | None:
        return sku.upper() if sku is not None else None

    @model_validator(mode="after")
    def validar_alteracoes(self) -> "ProdutoAtualizacao":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Os campos informados nao podem ser nulos.")
        return self


class ProdutoResposta(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade_estoque: int
    criado_em: datetime
    atualizado_em: datetime
