from fastapi import APIRouter

from app.api.routes import categorias, fornecedores, movimentacoes, produtos

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(categorias.router)
api_router.include_router(fornecedores.router)
api_router.include_router(produtos.router)
api_router.include_router(movimentacoes.router)

