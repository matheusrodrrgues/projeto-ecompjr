"""Funções de hash de senha e criação e leitura dos tokens JWT."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITMO_JWT = "HS256"
# O modo recomendado do pwdlib usa Argon2 e já define custo, salt e parâmetros seguros.
password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    """Recebe a senha em texto e devolve o hash Argon2 que será salvo no banco."""

    return password_hash.hash(senha)


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    """Pede ao pwdlib para comparar a senha do login com o hash cadastrado."""

    return password_hash.verify(senha, hash_salvo)


def criar_token(usuario_id: int) -> str:
    """Monta os dados do JWT e os assina com a chave definida no .env.

    O campo ``sub`` identifica o usuário, ``iat`` registra a emissão e ``exp``
    faz o token parar de funcionar depois do tempo configurado.
    """

    agora = datetime.now(UTC)
    dados = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expiracao_minutos),
    }
    return jwt.encode(dados, settings.jwt_secret, algorithm=ALGORITMO_JWT)


def ler_token(token: str) -> int:
    """Decodifica o JWT, confere assinatura e expiração e devolve o ID do usuário."""

    # Informar o algoritmo impede que o próprio token escolha como será validado.
    dados = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITMO_JWT],
        options={"require": ["sub", "exp"]},
    )
    return int(dados["sub"])
