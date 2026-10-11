from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoErro, NaoAutorizadoErro
from app.core.security import criar_token, gerar_hash_senha, verificar_senha
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCriacao


def criar_usuario(db: Session, dados: UsuarioCriacao) -> Usuario:
    existente = db.scalar(select(Usuario).where(Usuario.email == str(dados.email)))
    if existente is not None:
        raise ConflitoErro("EMAIL_DUPLICADO", "Já existe um usuário com esse e-mail.")

    usuario = Usuario(
        nome=dados.nome,
        email=str(dados.email),
        senha_hash=gerar_hash_senha(dados.senha),
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflitoErro("EMAIL_DUPLICADO", "Já existe um usuário com esse e-mail.") from None

    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> str:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutorizadoErro("E-mail ou senha inválidos.")
    return criar_token(usuario.id)
