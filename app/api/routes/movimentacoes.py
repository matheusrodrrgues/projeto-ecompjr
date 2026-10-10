from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.movimentacao import TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCriacao, MovimentacaoResposta
from app.services import movimentacoes as servico

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações de estoque"])
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post("", response_model=MovimentacaoResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: MovimentacaoCriacao, db: SessaoBanco) -> MovimentacaoResposta:
    return servico.criar_movimentacao(db, dados)


@router.get("", response_model=list[MovimentacaoResposta])
def listar(
    db: SessaoBanco,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fornecedor_id: Annotated[int | None, Query(gt=0)] = None,
    produto_id: Annotated[int | None, Query(gt=0)] = None,
    tipo: TipoMovimentacao | None = None,
) -> list[MovimentacaoResposta]:
    return servico.listar_movimentacoes(
        db,
        offset=offset,
        limite=limite,
        data_inicio=data_inicio,
        data_fim=data_fim,
        fornecedor_id=fornecedor_id,
        produto_id=produto_id,
        tipo=tipo,
    )


@router.get("/{movimentacao_id}", response_model=MovimentacaoResposta)
def buscar(movimentacao_id: int, db: SessaoBanco) -> MovimentacaoResposta:
    return servico.buscar_movimentacao(db, movimentacao_id)
