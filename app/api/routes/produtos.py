from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import obter_usuario_atual
from app.db.session import get_db
from app.schemas.produto import ProdutoAtualizacao, ProdutoCriacao, ProdutoResposta
from app.services import produtos as servico

router = APIRouter(prefix="/produtos", tags=["Produtos"])
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(obter_usuario_atual)],
)
def criar(dados: ProdutoCriacao, db: SessaoBanco) -> ProdutoResposta:
    return servico.criar_produto(db, dados)


@router.get("", response_model=list[ProdutoResposta])
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
    nome: str | None = None,
    categoria_id: Annotated[int | None, Query(gt=0)] = None,
    fornecedor_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[ProdutoResposta]:
    return servico.listar_produtos(
        db,
        offset=offset,
        limite=limite,
        nome=nome,
        categoria_id=categoria_id,
        fornecedor_id=fornecedor_id,
    )


@router.get("/estoque-baixo", response_model=list[ProdutoResposta])
def listar_estoque_baixo(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ProdutoResposta]:
    return servico.listar_estoque_baixo(db, offset, limite)


@router.get("/{produto_id}", response_model=ProdutoResposta)
def buscar(produto_id: int, db: SessaoBanco) -> ProdutoResposta:
    return servico.buscar_produto(db, produto_id)


@router.patch(
    "/{produto_id}",
    response_model=ProdutoResposta,
    dependencies=[Depends(obter_usuario_atual)],
)
def atualizar(produto_id: int, dados: ProdutoAtualizacao, db: SessaoBanco) -> ProdutoResposta:
    return servico.atualizar_produto(db, produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(obter_usuario_atual)],
)
def excluir(produto_id: int, db: SessaoBanco) -> Response:
    servico.excluir_produto(db, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
