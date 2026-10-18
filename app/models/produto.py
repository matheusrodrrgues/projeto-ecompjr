from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.fornecedor import Fornecedor
    from app.models.movimentacao import MovimentacaoEstoque


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("preco_custo >= 0", name="ck_produto_preco_custo_nao_negativo"),
        CheckConstraint("preco_venda >= 0", name="ck_produto_preco_venda_nao_negativo"),
        CheckConstraint(
            "quantidade_estoque >= 0", name="ck_produto_quantidade_estoque_nao_negativa"
        ),
        CheckConstraint("estoque_minimo >= 0", name="ck_produto_estoque_minimo_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantidade_estoque: Mapped[int] = mapped_column(default=0, server_default="0")
    estoque_minimo: Mapped[int] = mapped_column(default=0, server_default="0")
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"), index=True
    )
    fornecedor_id: Mapped[int] = mapped_column(
        ForeignKey("fornecedores.id", ondelete="RESTRICT"), index=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    categoria: Mapped[Categoria] = relationship(back_populates="produtos")
    fornecedor: Mapped[Fornecedor] = relationship(back_populates="produtos")
    movimentacoes: Mapped[list[MovimentacaoEstoque]] = relationship(back_populates="produto")
