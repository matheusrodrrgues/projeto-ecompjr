from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoErro, RecursoNaoEncontradoErro
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto
from app.schemas.fornecedor import FornecedorAtualizacao, FornecedorCriacao


def _verificar_duplicidade(
    db: Session, cnpj: str | None, email: str | None, ignorar_id: int | None = None
) -> None:
    filtros = []
    if cnpj is not None:
        filtros.append(Fornecedor.cnpj == cnpj)
    if email is not None:
        filtros.append(Fornecedor.email == email)
    if not filtros:
        return

    consulta = select(Fornecedor).where(or_(*filtros))
    if ignorar_id is not None:
        consulta = consulta.where(Fornecedor.id != ignorar_id)

    existente = db.scalar(consulta)
    if existente is None:
        return
    if cnpj is not None and existente.cnpj == cnpj:
        raise ConflitoErro("CNPJ_DUPLICADO", "Ja existe um fornecedor com esse CNPJ.")
    raise ConflitoErro("EMAIL_DUPLICADO", "Ja existe um fornecedor com esse e-mail.")


def criar_fornecedor(db: Session, dados: FornecedorCriacao) -> Fornecedor:
    _verificar_duplicidade(db, dados.cnpj, str(dados.email))
    fornecedor = Fornecedor(
        nome=dados.nome,
        cnpj=dados.cnpj,
        telefone=dados.telefone,
        email=str(dados.email),
    )
    db.add(fornecedor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro("FORNECEDOR_DUPLICADO", "CNPJ ou e-mail ja cadastrado.") from None

    db.refresh(fornecedor)
    return fornecedor


def listar_fornecedores(db: Session, offset: int, limite: int) -> list[Fornecedor]:
    consulta = select(Fornecedor).order_by(Fornecedor.id).offset(offset).limit(limite)
    return list(db.scalars(consulta))


def buscar_fornecedor(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise RecursoNaoEncontradoErro("Fornecedor")
    return fornecedor


def atualizar_fornecedor(
    db: Session, fornecedor_id: int, dados: FornecedorAtualizacao
) -> Fornecedor:
    fornecedor = buscar_fornecedor(db, fornecedor_id)
    alteracoes = dados.model_dump(exclude_unset=True)

    novo_email = alteracoes.get("email")
    if novo_email is not None:
        novo_email = str(novo_email)
        alteracoes["email"] = novo_email

    _verificar_duplicidade(
        db,
        alteracoes.get("cnpj"),
        novo_email,
        ignorar_id=fornecedor_id,
    )

    for campo, valor in alteracoes.items():
        setattr(fornecedor, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro("FORNECEDOR_DUPLICADO", "CNPJ ou e-mail ja cadastrado.") from None

    db.refresh(fornecedor)
    return fornecedor


def excluir_fornecedor(db: Session, fornecedor_id: int) -> None:
    fornecedor = buscar_fornecedor(db, fornecedor_id)
    produto_vinculado = db.scalar(
        select(Produto.id).where(Produto.fornecedor_id == fornecedor_id).limit(1)
    )
    if produto_vinculado is not None:
        raise ConflitoErro(
            "FORNECEDOR_EM_USO",
            "O fornecedor possui produtos vinculados e nao pode ser excluido.",
        )

    db.delete(fornecedor)
    db.commit()
