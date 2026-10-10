"""Guarda o fornecedor no historico de movimentacoes.

Revision ID: 20261010_02
Revises: 20261010_01
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261010_02"
down_revision: str | None = "20261010_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "movimentacoes_estoque",
        sa.Column("fornecedor_id", sa.Integer(), nullable=True),
    )

    # Copia o fornecedor atual para preservar qualquer movimentacao que ja exista.
    op.execute(
        sa.text(
            """
            UPDATE movimentacoes_estoque AS movimentacao
            SET fornecedor_id = produto.fornecedor_id
            FROM produtos AS produto
            WHERE produto.id = movimentacao.produto_id
            """
        )
    )

    op.alter_column("movimentacoes_estoque", "fornecedor_id", nullable=False)
    op.create_foreign_key(
        "fk_movimentacoes_fornecedor",
        "movimentacoes_estoque",
        "fornecedores",
        ["fornecedor_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_movimentacoes_estoque_fornecedor_id",
        "movimentacoes_estoque",
        ["fornecedor_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_movimentacoes_estoque_fornecedor_id",
        table_name="movimentacoes_estoque",
    )
    op.drop_constraint(
        "fk_movimentacoes_fornecedor",
        "movimentacoes_estoque",
        type_="foreignkey",
    )
    op.drop_column("movimentacoes_estoque", "fornecedor_id")
