from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fornecedor import (
    FornecedorAtualizacao,
    FornecedorCriacao,
    FornecedorResposta,
)
from app.services import fornecedores as servico

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post("", response_model=FornecedorResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: FornecedorCriacao, db: SessaoBanco) -> FornecedorResposta:
    return servico.criar_fornecedor(db, dados)


@router.get("", response_model=list[FornecedorResposta])
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[FornecedorResposta]:
    return servico.listar_fornecedores(db, offset, limite)


@router.get("/{fornecedor_id}", response_model=FornecedorResposta)
def buscar(fornecedor_id: int, db: SessaoBanco) -> FornecedorResposta:
    return servico.buscar_fornecedor(db, fornecedor_id)


@router.patch("/{fornecedor_id}", response_model=FornecedorResposta)
def atualizar(
    fornecedor_id: int, dados: FornecedorAtualizacao, db: SessaoBanco
) -> FornecedorResposta:
    return servico.atualizar_fornecedor(db, fornecedor_id, dados)


@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(fornecedor_id: int, db: SessaoBanco) -> Response:
    servico.excluir_fornecedor(db, fornecedor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
