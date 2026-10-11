"""Endpoints de criação, consulta, atualização e exclusão de categorias."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import obter_usuario_atual
from app.api.documentacao import RESPOSTAS_COMUNS, respostas
from app.db.session import get_db
from app.schemas.categoria import (
    CategoriaAtualizacao,
    CategoriaCriacao,
    CategoriaResposta,
)
from app.services import categorias as servico

router = APIRouter(prefix="/categorias", tags=["Categorias"], responses=RESPOSTAS_COMUNS)
# Ao encontrar SessaoBanco, o FastAPI chama get_db e injeta a sessão na rota.
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=CategoriaResposta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Cadastrar categoria",
    responses=respostas(401, 409),
)
def criar(dados: CategoriaCriacao, db: SessaoBanco) -> CategoriaResposta:
    """Valida o nome e chama ``criar_categoria``, que impede nomes repetidos."""

    return servico.criar_categoria(db, dados)


@router.get("", response_model=list[CategoriaResposta], summary="Listar categorias")
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[CategoriaResposta]:
    """Consulta categorias por ordem de ID usando a paginação recebida na URL."""

    return servico.listar_categorias(db, offset, limite)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResposta,
    summary="Consultar categoria",
    responses=respostas(404),
)
def buscar(categoria_id: int, db: SessaoBanco) -> CategoriaResposta:
    """Chama ``buscar_categoria``; o service devolve o registro ou um erro 404."""

    return servico.buscar_categoria(db, categoria_id)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaResposta,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Atualizar categoria",
    responses=respostas(401, 404, 409),
)
def atualizar(categoria_id: int, dados: CategoriaAtualizacao, db: SessaoBanco) -> CategoriaResposta:
    """Envia o ID e o novo nome ao service, que confere existência e duplicidade."""

    return servico.atualizar_categoria(db, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Excluir categoria",
    responses=respostas(401, 404, 409),
)
def excluir(categoria_id: int, db: SessaoBanco) -> Response:
    """Exclui pelo ID somente se nenhum produto usar a categoria e retorna 204."""

    servico.excluir_categoria(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
