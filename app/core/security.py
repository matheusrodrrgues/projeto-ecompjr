from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITMO_JWT = "HS256"
password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    return password_hash.verify(senha, hash_salvo)


def criar_token(usuario_id: int) -> str:
    agora = datetime.now(UTC)
    dados = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expiracao_minutos),
    }
    return jwt.encode(dados, settings.jwt_secret, algorithm=ALGORITMO_JWT)


def ler_token(token: str) -> int:
    # O algoritmo fica definido aqui para não ser escolhido pelo próprio token.
    dados = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITMO_JWT],
        options={"require": ["sub", "exp"]},
    )
    return int(dados["sub"])
