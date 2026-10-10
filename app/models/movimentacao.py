from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        SqlEnum(TipoMovimentacao, name="tipo_movimentacao")
    )
    quantidade: Mapped[int]
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    produto: Mapped["Produto"] = relationship(back_populates="movimentacoes")

