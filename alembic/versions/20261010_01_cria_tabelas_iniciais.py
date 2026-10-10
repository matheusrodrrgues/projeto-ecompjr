"""Cria as tabelas iniciais do estoque.

Revision ID: 20261010_01
Revises:
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261010_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categorias_nome", "categorias", ["nome"], unique=True)

    op.create_table(
        "fornecedores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=False),
        sa.Column("telefone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fornecedores_cnpj", "fornecedores", ["cnpj"], unique=True)
    op.create_index("ix_fornecedores_email", "fornecedores", ["email"], unique=True)

    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("preco_custo", sa.Numeric(12, 2), nullable=False),
        sa.Column("preco_venda", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantidade_estoque", sa.Integer(), server_default="0", nullable=False),
        sa.Column("estoque_minimo", sa.Integer(), server_default="0", nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("fornecedor_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("estoque_minimo >= 0", name="ck_produto_estoque_minimo_nao_negativo"),
        sa.CheckConstraint("preco_custo >= 0", name="ck_produto_preco_custo_nao_negativo"),
        sa.CheckConstraint("preco_venda >= 0", name="ck_produto_preco_venda_nao_negativo"),
        sa.CheckConstraint(
            "quantidade_estoque >= 0", name="ck_produto_quantidade_estoque_nao_negativa"
        ),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["fornecedor_id"], ["fornecedores.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_produtos_categoria_id", "produtos", ["categoria_id"])
    op.create_index("ix_produtos_fornecedor_id", "produtos", ["fornecedor_id"])
    op.create_index("ix_produtos_sku", "produtos", ["sku"], unique=True)

    tipo_movimentacao = sa.Enum("entrada", "saida", name="tipo_movimentacao")
    op.create_table(
        "movimentacoes_estoque",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("tipo", tipo_movimentacao, nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("data", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade_positiva"),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_movimentacoes_estoque_produto_id",
        "movimentacoes_estoque",
        ["produto_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_movimentacoes_estoque_produto_id", table_name="movimentacoes_estoque")
    op.drop_table("movimentacoes_estoque")
    sa.Enum(name="tipo_movimentacao").drop(op.get_bind(), checkfirst=True)
    op.drop_index("ix_produtos_sku", table_name="produtos")
    op.drop_index("ix_produtos_fornecedor_id", table_name="produtos")
    op.drop_index("ix_produtos_categoria_id", table_name="produtos")
    op.drop_table("produtos")
    op.drop_index("ix_fornecedores_email", table_name="fornecedores")
    op.drop_index("ix_fornecedores_cnpj", table_name="fornecedores")
    op.drop_table("fornecedores")
    op.drop_index("ix_categorias_nome", table_name="categorias")
    op.drop_table("categorias")
