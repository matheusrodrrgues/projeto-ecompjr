from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fornecedor import Fornecedor
    from app.models.produto import Produto


class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="RESTRICT"), index=True
    )
    fornecedor_id: Mapped[int] = mapped_column(
        ForeignKey("fornecedores.id", ondelete="RESTRICT"), index=True
    )
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        SqlEnum(
            TipoMovimentacao,
            name="tipo_movimentacao",
            values_callable=lambda tipos: [tipo.value for tipo in tipos],
        )
    )
    quantidade: Mapped[int]
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    produto: Mapped[Produto] = relationship(back_populates="movimentacoes")
    fornecedor: Mapped[Fornecedor] = relationship(back_populates="movimentacoes")
