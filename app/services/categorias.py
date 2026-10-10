from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoErro, RecursoNaoEncontradoErro
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.schemas.categoria import CategoriaAtualizacao, CategoriaCriacao


def criar_categoria(db: Session, dados: CategoriaCriacao) -> Categoria:
    existente = db.scalar(select(Categoria).where(Categoria.nome == dados.nome))
    if existente:
        raise ConflitoErro("CATEGORIA_DUPLICADA", "Já existe uma categoria com esse nome.")

    categoria = Categoria(nome=dados.nome)
    db.add(categoria)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro(
            "CATEGORIA_DUPLICADA", "Já existe uma categoria com esse nome."
        ) from None

    db.refresh(categoria)
    return categoria


def listar_categorias(db: Session, offset: int, limite: int) -> list[Categoria]:
    consulta = select(Categoria).order_by(Categoria.id).offset(offset).limit(limite)
    return list(db.scalars(consulta))


def buscar_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise RecursoNaoEncontradoErro("Categoria")
    return categoria


def atualizar_categoria(db: Session, categoria_id: int, dados: CategoriaAtualizacao) -> Categoria:
    categoria = buscar_categoria(db, categoria_id)
    alteracoes = dados.model_dump(exclude_unset=True)

    if "nome" in alteracoes:
        existente = db.scalar(
            select(Categoria).where(
                Categoria.nome == alteracoes["nome"], Categoria.id != categoria_id
            )
        )
        if existente:
            raise ConflitoErro("CATEGORIA_DUPLICADA", "Já existe uma categoria com esse nome.")
        categoria.nome = alteracoes["nome"]

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro(
            "CATEGORIA_DUPLICADA", "Já existe uma categoria com esse nome."
        ) from None

    db.refresh(categoria)
    return categoria


def excluir_categoria(db: Session, categoria_id: int) -> None:
    categoria = buscar_categoria(db, categoria_id)
    produto_vinculado = db.scalar(
        select(Produto.id).where(Produto.categoria_id == categoria_id).limit(1)
    )
    if produto_vinculado is not None:
        raise ConflitoErro(
            "CATEGORIA_EM_USO", "A categoria possui produtos vinculados e não pode ser excluída."
        )

    db.delete(categoria)
    db.commit()
