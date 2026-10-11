"""Dependências compartilhadas pelas rotas protegidas."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.exceptions import NaoAutorizadoErro
from app.core.security import ler_token
from app.db.session import get_db
from app.models.usuario import Usuario

# O FastAPI lê o cabeçalho Authorization e também cria o botão Authorize no Swagger.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def obter_usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    """Valida o Bearer token antes de uma rota protegida ser executada.

    ``oauth2_scheme`` entrega o token, ``ler_token`` recupera o ID e a sessão
    consulta o usuário. Qualquer falha encerra a requisição com status 401.
    """

    try:
        usuario_id = ler_token(token)
    except (InvalidTokenError, TypeError, ValueError):
        raise NaoAutorizadoErro("Token inválido ou expirado.") from None

    # A consulta evita aceitar um token antigo de um usuário que deixou de existir.
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoAutorizadoErro("Token inválido ou expirado.")
    return usuario
