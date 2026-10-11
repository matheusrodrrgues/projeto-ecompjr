"""Endpoints de criação, consulta, atualização e exclusão de fornecedores."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import obter_usuario_atual
from app.api.documentacao import RESPOSTAS_COMUNS, respostas
from app.db.session import get_db
from app.schemas.fornecedor import (
    FornecedorAtualizacao,
    FornecedorCriacao,
    FornecedorResposta,
)
from app.services import fornecedores as servico

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"], responses=RESPOSTAS_COMUNS)
# Ao encontrar SessaoBanco, o FastAPI chama get_db e injeta a sessão na rota.
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=FornecedorResposta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Cadastrar fornecedor",
    responses=respostas(401, 409),
)
def criar(dados: FornecedorCriacao, db: SessaoBanco) -> FornecedorResposta:
    """Cadastra os dados já normalizados, após conferir CNPJ e e-mail repetidos."""

    return servico.criar_fornecedor(db, dados)


@router.get("", response_model=list[FornecedorResposta], summary="Listar fornecedores")
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[FornecedorResposta]:
    """Consulta fornecedores por ordem de ID usando a paginação recebida na URL."""

    return servico.listar_fornecedores(db, offset, limite)


@router.get(
    "/{fornecedor_id}",
    response_model=FornecedorResposta,
    summary="Consultar fornecedor",
    responses=respostas(404),
)
def buscar(fornecedor_id: int, db: SessaoBanco) -> FornecedorResposta:
    """Chama ``buscar_fornecedor``; o service devolve o registro ou um erro 404."""

    return servico.buscar_fornecedor(db, fornecedor_id)


@router.patch(
    "/{fornecedor_id}",
    response_model=FornecedorResposta,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Atualizar fornecedor",
    responses=respostas(401, 404, 409),
)
def atualizar(
    fornecedor_id: int, dados: FornecedorAtualizacao, db: SessaoBanco
) -> FornecedorResposta:
    """Atualiza os campos enviados depois de conferir novo CNPJ e novo e-mail."""

    return servico.atualizar_fornecedor(db, fornecedor_id, dados)


@router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(obter_usuario_atual)],
    summary="Excluir fornecedor",
    responses=respostas(401, 404, 409),
)
def excluir(fornecedor_id: int, db: SessaoBanco) -> Response:
    """Exclui somente sem produto ou movimentação vinculada e então retorna 204."""

    servico.excluir_fornecedor(db, fornecedor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
