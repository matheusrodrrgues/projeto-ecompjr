"""Endpoints do catálogo e das consultas de estoque baixo."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import obter_usuario_atual
from app.api.documentacao import RESPOSTAS_COMUNS, respostas
from app.db.session import get_db
from app.schemas.produto import ProdutoAtualizacao, ProdutoCriacao, ProdutoResposta
from app.services import produtos as servico

router = APIRouter(prefix="/produtos", tags=["Produtos"], responses=RESPOSTAS_COMUNS)
# Ao encontrar SessaoBanco, o FastAPI chama get_db e injeta a sessão na rota.
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Cadastrar produto",
    responses=respostas(401, 404, 409),
)
def criar(dados: ProdutoCriacao, db: SessaoBanco) -> ProdutoResposta:
    """Confere categoria, fornecedor e SKU antes de criar o produto com saldo zero."""

    return servico.criar_produto(db, dados)


@router.get("", response_model=list[ProdutoResposta], summary="Listar e filtrar produtos")
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
    nome: str | None = None,
    categoria_id: Annotated[int | None, Query(gt=0)] = None,
    fornecedor_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[ProdutoResposta]:
    """Busca produtos por nome, categoria ou fornecedor e aplica a paginação."""

    return servico.listar_produtos(
        db,
        offset=offset,
        limite=limite,
        nome=nome,
        categoria_id=categoria_id,
        fornecedor_id=fornecedor_id,
    )


@router.get(
    "/estoque-baixo",
    response_model=list[ProdutoResposta],
    summary="Listar produtos com estoque baixo",
)
def listar_estoque_baixo(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ProdutoResposta]:
    """Lista produtos cujo saldo atual está abaixo ou igual ao estoque mínimo."""

    return servico.listar_estoque_baixo(db, offset, limite)


@router.get(
    "/{produto_id}",
    response_model=ProdutoResposta,
    summary="Consultar produto",
    responses=respostas(404),
)
def buscar(produto_id: int, db: SessaoBanco) -> ProdutoResposta:
    """Chama ``buscar_produto``; o service devolve o registro ou um erro 404."""

    return servico.buscar_produto(db, produto_id)


@router.patch(
    "/{produto_id}",
    response_model=ProdutoResposta,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Atualizar produto",
    responses=respostas(401, 404, 409),
)
def atualizar(produto_id: int, dados: ProdutoAtualizacao, db: SessaoBanco) -> ProdutoResposta:
    """Atualiza somente os campos enviados, mas nunca altera o saldo por esta rota."""

    return servico.atualizar_produto(db, produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Excluir produto",
    responses=respostas(401, 404, 409),
)
def excluir(produto_id: int, db: SessaoBanco) -> Response:
    """Exclui somente produtos sem movimentação, preservando o histórico de estoque."""

    servico.excluir_produto(db, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
