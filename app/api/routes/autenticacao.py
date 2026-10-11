"""Endpoints públicos de cadastro e login."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.documentacao import RESPOSTAS_COMUNS, respostas
from app.db.session import get_db
from app.schemas.usuario import TokenResposta, UsuarioCriacao, UsuarioResposta
from app.services import autenticacao as servico

router = APIRouter(prefix="/auth", tags=["Autenticação"], responses=RESPOSTAS_COMUNS)
# Ao encontrar SessaoBanco, o FastAPI chama get_db e injeta a sessão na rota.
SessaoBanco = Annotated[Session, Depends(get_db)]


@router.post(
    "/cadastro",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    responses=respostas(409),
)
def cadastrar(dados: UsuarioCriacao, db: SessaoBanco) -> UsuarioResposta:
    """Cadastra um usuário e devolve somente os campos públicos.

    O FastAPI valida o JSON com ``UsuarioCriacao``. Depois, ``criar_usuario``
    verifica o e-mail, gera o hash da senha e salva o registro. O schema
    ``UsuarioResposta`` não possui o hash, então ele não aparece na resposta.
    """

    return servico.criar_usuario(db, dados)


@router.post(
    "/login",
    response_model=TokenResposta,
    summary="Entrar e gerar token JWT",
    description="No campo username, informe o e-mail usado no cadastro.",
    responses=respostas(401),
)
def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessaoBanco,
) -> TokenResposta:
    """Troca e-mail e senha por um token JWT.

    O formulário OAuth2 chama o campo de e-mail de ``username``. O service
    busca esse e-mail, compara a senha com o hash salvo e cria o token.
    """

    token = servico.autenticar(db, formulario.username, formulario.password)
    return TokenResposta(access_token=token)
