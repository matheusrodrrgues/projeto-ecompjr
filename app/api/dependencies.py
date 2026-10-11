from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.exceptions import NaoAutorizadoErro
from app.core.security import ler_token
from app.db.session import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def obter_usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    try:
        usuario_id = ler_token(token)
    except (InvalidTokenError, TypeError, ValueError):
        raise NaoAutorizadoErro("Token inválido ou expirado.") from None

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoAutorizadoErro("Token inválido ou expirado.")
    return usuario
