"""Validação dos dados usados no cadastro de produtos."""

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

    @field_validator("nome", "sku", mode="before")
    @classmethod
    def limpar_texto(cls, valor: str) -> str:
        """Remove espaços das pontas antes de validar nome e SKU."""
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("sku")
    @classmethod
    def padronizar_sku(cls, sku: str) -> str:
        """Converte o SKU para maiúsculas para evitar duplicidade por capitalização."""
        return sku.upper()


class ProdutoCriacao(ProdutoBase):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "nome": "Caderno universitário",
                    "sku": "CAD-001",
                    "preco_custo": "10.00",
                    "preco_venda": "18.00",
                    "estoque_minimo": 5,
                    "categoria_id": 1,
                    "fornecedor_id": 1,
                }
            ]
        },
    )


class ProdutoAtualizacao(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"preco_venda": "19.90", "estoque_minimo": 8}]},
    )

    nome: str | None = Field(default=None, min_length=2, max_length=150)
    sku: str | None = Field(default=None, min_length=2, max_length=50)
    preco_custo: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    estoque_minimo: int | None = Field(default=None, ge=0)
    categoria_id: int | None = Field(default=None, gt=0)
    fornecedor_id: int | None = Field(default=None, gt=0)

    @field_validator("nome", "sku", mode="before")
    @classmethod
    def limpar_texto(cls, valor: str | None) -> str | None:
        """Limpa os textos recebidos sem preencher campos ausentes no PATCH."""
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("sku")
    @classmethod
    def padronizar_sku(cls, sku: str | None) -> str | None:
        """Mantém o padrão em maiúsculas quando um novo SKU é informado."""
        return sku.upper() if sku is not None else None

    @model_validator(mode="after")
    def validar_alteracoes(self) -> "ProdutoAtualizacao":
        """Rejeita atualizações vazias e campos explicitamente enviados como nulos."""
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Os campos informados não podem ser nulos.")
        return self


class ProdutoResposta(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade_estoque: int
    criado_em: datetime
    atualizado_em: datetime
