"""Criação da aplicação e tratamento centralizado dos erros HTTP."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import RegraDeNegocioErro

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "API para cadastro do catálogo e controle das entradas e saídas "
        "de estoque de uma loja de variedades."
    ),
)
app.include_router(api_router)
logger = logging.getLogger(__name__)


@app.exception_handler(RegraDeNegocioErro)
async def tratar_erro_de_negocio(request: Request, erro: RegraDeNegocioErro) -> JSONResponse:
    """Converte erros previstos pelos services para o padrão JSON da API."""

    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": {"codigo": erro.codigo, "mensagem": erro.mensagem}},
        headers=erro.headers,
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(request: Request, erro: RequestValidationError) -> JSONResponse:
    """Transforma os erros do Pydantic em uma lista simples de campo e mensagem."""

    detalhes = [
        {
            "campo": ".".join(str(parte) for parte in item["loc"][1:]),
            "mensagem": item["msg"],
        }
        for item in erro.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "erro": {
                "codigo": "DADOS_INVALIDOS",
                "mensagem": "Confira os dados enviados.",
                "detalhes": detalhes,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(request: Request, erro: StarletteHTTPException) -> JSONResponse:
    """Padroniza erros gerados pelo roteamento, como rota ou método inexistente."""

    mensagens = {
        404: "Rota não encontrada.",
        405: "Método não permitido.",
    }
    mensagem = mensagens.get(erro.status_code, str(erro.detail))
    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": {"codigo": "ERRO_HTTP", "mensagem": mensagem}},
    )


@app.exception_handler(Exception)
async def tratar_erro_inesperado(request: Request, erro: Exception) -> JSONResponse:
    """Registra o erro completo no servidor sem expor detalhes internos ao cliente."""

    logger.exception("Erro inesperado durante a requisição", exc_info=erro)
    return JSONResponse(
        status_code=500,
        content={
            "erro": {
                "codigo": "ERRO_INTERNO",
                "mensagem": "Ocorreu um erro interno. Tente novamente mais tarde.",
            }
        },
    )


@app.get(
    "/health",
    tags=["Saúde"],
    summary="Verificar se a API está disponível",
)
async def health_check() -> dict[str, str]:
    """Resposta leve usada para confirmar que o processo da API está ativo."""

    return {"status": "ok"}
