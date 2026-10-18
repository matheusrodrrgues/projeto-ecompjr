from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.movimentacao import TipoMovimentacao


class MovimentacaoCriacao(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "produto_id": 1,
                    "tipo": "entrada",
                    "quantidade": 20,
                    "observacao": "Compra do fornecedor",
                }
            ]
        },
    )

    produto_id: int = Field(gt=0)
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    observacao: str | None = Field(default=None, max_length=500)

    @field_validator("observacao", mode="before")
    @classmethod
    def limpar_observacao(cls, observacao: str | None) -> str | None:
        if observacao is None:
            return None
        if not isinstance(observacao, str):
            return observacao
        observacao = observacao.strip()
        return observacao or None


class MovimentacaoResposta(MovimentacaoCriacao):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fornecedor_id: int
    data: datetime
