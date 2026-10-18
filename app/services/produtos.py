from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoErro, RecursoNaoEncontradoErro
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.models.movimentacao import MovimentacaoEstoque
from app.models.produto import Produto
from app.schemas.produto import ProdutoAtualizacao, ProdutoCriacao


def _verificar_relacionamentos(db: Session, categoria_id: int, fornecedor_id: int) -> None:
    if db.get(Categoria, categoria_id) is None:
        raise RecursoNaoEncontradoErro("Categoria")
    if db.get(Fornecedor, fornecedor_id) is None:
        raise RecursoNaoEncontradoErro("Fornecedor")


def _verificar_sku(db: Session, sku: str, ignorar_produto_id: int | None = None) -> None:
    consulta = select(Produto).where(Produto.sku == sku)
    if ignorar_produto_id is not None:
        consulta = consulta.where(Produto.id != ignorar_produto_id)
    if db.scalar(consulta) is not None:
        raise ConflitoErro("SKU_DUPLICADO", "Já existe um produto com esse SKU.")


def criar_produto(db: Session, dados: ProdutoCriacao) -> Produto:
    _verificar_relacionamentos(db, dados.categoria_id, dados.fornecedor_id)
    _verificar_sku(db, dados.sku)

    # O estoque só pode mudar quando uma movimentação é registrada.
    produto = Produto(**dados.model_dump(), quantidade_estoque=0)
    db.add(produto)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro("PRODUTO_INVALIDO", "Não foi possível cadastrar o produto.") from None

    db.refresh(produto)
    return produto


def listar_produtos(
    db: Session,
    offset: int,
    limite: int,
    nome: str | None = None,
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
) -> list[Produto]:
    consulta = select(Produto)
    if nome:
        consulta = consulta.where(Produto.nome.ilike(f"%{nome.strip()}%"))
    if categoria_id is not None:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    if fornecedor_id is not None:
        consulta = consulta.where(Produto.fornecedor_id == fornecedor_id)

    consulta = consulta.order_by(Produto.id).offset(offset).limit(limite)
    return list(db.scalars(consulta))


def listar_estoque_baixo(db: Session, offset: int, limite: int) -> list[Produto]:
    consulta = (
        select(Produto)
        .where(Produto.quantidade_estoque <= Produto.estoque_minimo)
        .order_by(Produto.id)
        .offset(offset)
        .limit(limite)
    )
    return list(db.scalars(consulta))


def buscar_produto(db: Session, produto_id: int) -> Produto:
    produto = db.get(Produto, produto_id)
    if produto is None:
        raise RecursoNaoEncontradoErro("Produto")
    return produto


def atualizar_produto(db: Session, produto_id: int, dados: ProdutoAtualizacao) -> Produto:
    produto = buscar_produto(db, produto_id)
    alteracoes = dados.model_dump(exclude_unset=True)

    categoria_id = alteracoes.get("categoria_id", produto.categoria_id)
    fornecedor_id = alteracoes.get("fornecedor_id", produto.fornecedor_id)
    _verificar_relacionamentos(db, categoria_id, fornecedor_id)

    if "sku" in alteracoes:
        _verificar_sku(db, alteracoes["sku"], ignorar_produto_id=produto_id)

    for campo, valor in alteracoes.items():
        setattr(produto, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro("PRODUTO_INVALIDO", "Não foi possível atualizar o produto.") from None

    db.refresh(produto)
    return produto


def excluir_produto(db: Session, produto_id: int) -> None:
    produto = buscar_produto(db, produto_id)
    movimentacao = db.scalar(
        select(MovimentacaoEstoque.id).where(MovimentacaoEstoque.produto_id == produto_id).limit(1)
    )
    if movimentacao is not None:
        raise ConflitoErro(
            "PRODUTO_COM_HISTORICO",
            "O produto possui movimentações e não pode ser excluído.",
        )

    db.delete(produto)
    db.commit()
