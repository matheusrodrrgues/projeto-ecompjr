import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import RegraDeNegocioErro

app = FastAPI(title=settings.app_name)
app.include_router(api_router)
logger = logging.getLogger(__name__)


@app.exception_handler(RegraDeNegocioErro)
async def tratar_erro_de_negocio(request: Request, erro: RegraDeNegocioErro) -> JSONResponse:
    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": {"codigo": erro.codigo, "mensagem": erro.mensagem}},
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(request: Request, erro: RequestValidationError) -> JSONResponse:
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
    mensagem = "Rota nao encontrada." if erro.status_code == 404 else str(erro.detail)
    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": {"codigo": "ERRO_HTTP", "mensagem": mensagem}},
    )


@app.exception_handler(Exception)
async def tratar_erro_inesperado(request: Request, erro: Exception) -> JSONResponse:
    logger.exception("Erro inesperado durante a requisicao", exc_info=erro)
    return JSONResponse(
        status_code=500,
        content={
            "erro": {
                "codigo": "ERRO_INTERNO",
                "mensagem": "Ocorreu um erro interno. Tente novamente mais tarde.",
            }
        },
    )


@app.get("/health", tags=["Saude"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
