from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import RegraDeNegocioErro

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.exception_handler(RegraDeNegocioErro)
async def tratar_erro_de_negocio(request: Request, erro: RegraDeNegocioErro) -> JSONResponse:
    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": {"codigo": erro.codigo, "mensagem": erro.mensagem}},
    )


@app.get("/health", tags=["Saude"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
