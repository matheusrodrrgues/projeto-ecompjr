from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import obter_usuario_atual
from app.db.session import get_db
from app.schemas.categoria import (
    CategoriaAtualizacao,
    CategoriaCriacao,
    CategoriaResposta,
)
from app.services import categorias as servico

router = APIRouter(prefix="/categorias", tags=["Categorias"])
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=CategoriaResposta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(obter_usuario_atual)],
)
def criar(dados: CategoriaCriacao, db: SessaoBanco) -> CategoriaResposta:
    return servico.criar_categoria(db, dados)


@router.get("", response_model=list[CategoriaResposta])
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[CategoriaResposta]:
    return servico.listar_categorias(db, offset, limite)


@router.get("/{categoria_id}", response_model=CategoriaResposta)
def buscar(categoria_id: int, db: SessaoBanco) -> CategoriaResposta:
    return servico.buscar_categoria(db, categoria_id)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaResposta,
    dependencies=[Depends(obter_usuario_atual)],
)
def atualizar(categoria_id: int, dados: CategoriaAtualizacao, db: SessaoBanco) -> CategoriaResposta:
    return servico.atualizar_categoria(db, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(obter_usuario_atual)],
)
def excluir(categoria_id: int, db: SessaoBanco) -> Response:
    servico.excluir_categoria(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
