from datetime import UTC, date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoErro, RecursoNaoEncontradoErro, RegraDeNegocioErro
from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao
from app.models.produto import Produto
from app.schemas.movimentacao import MovimentacaoCriacao


def criar_movimentacao(db: Session, dados: MovimentacaoCriacao) -> MovimentacaoEstoque:
    try:
        # O bloqueio impede duas saídas simultâneas de usarem o mesmo saldo.
        produto = db.scalar(select(Produto).where(Produto.id == dados.produto_id).with_for_update())
        if produto is None:
            raise RecursoNaoEncontradoErro("Produto")

        if dados.tipo == TipoMovimentacao.SAIDA and produto.quantidade_estoque < dados.quantidade:
            raise ConflitoErro(
                "ESTOQUE_INSUFICIENTE",
                "O produto não possui estoque suficiente para essa saída.",
            )

        if dados.tipo == TipoMovimentacao.ENTRADA:
            produto.quantidade_estoque += dados.quantidade
        else:
            produto.quantidade_estoque -= dados.quantidade

        movimentacao = MovimentacaoEstoque(
            produto_id=produto.id,
            fornecedor_id=produto.fornecedor_id,
            tipo=dados.tipo,
            quantidade=dados.quantidade,
            observacao=dados.observacao,
        )
        db.add(movimentacao)
        db.commit()
        db.refresh(movimentacao)
        return movimentacao
    except Exception:
        db.rollback()
        raise


def listar_movimentacoes(
    db: Session,
    offset: int,
    limite: int,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fornecedor_id: int | None = None,
    produto_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
) -> list[MovimentacaoEstoque]:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise RegraDeNegocioErro(
            "PERIODO_INVALIDO",
            "A data inicial não pode ser posterior à data final.",
        )

    consulta = select(MovimentacaoEstoque)
    if data_inicio:
        inicio = datetime.combine(data_inicio, time.min, tzinfo=UTC)
        consulta = consulta.where(MovimentacaoEstoque.data >= inicio)
    if data_fim:
        fim = datetime.combine(data_fim, time.max, tzinfo=UTC)
        consulta = consulta.where(MovimentacaoEstoque.data <= fim)
    if fornecedor_id is not None:
        consulta = consulta.where(MovimentacaoEstoque.fornecedor_id == fornecedor_id)
    if produto_id is not None:
        consulta = consulta.where(MovimentacaoEstoque.produto_id == produto_id)
    if tipo is not None:
        consulta = consulta.where(MovimentacaoEstoque.tipo == tipo)

    consulta = (
        consulta.order_by(MovimentacaoEstoque.data.desc(), MovimentacaoEstoque.id.desc())
        .offset(offset)
        .limit(limite)
    )
    return list(db.scalars(consulta))


def buscar_movimentacao(db: Session, movimentacao_id: int) -> MovimentacaoEstoque:
    movimentacao = db.get(MovimentacaoEstoque, movimentacao_id)
    if movimentacao is None:
        raise RecursoNaoEncontradoErro("Movimentação")
    return movimentacao
