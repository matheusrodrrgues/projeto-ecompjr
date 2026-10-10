from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.get("/health", tags=["Saude"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

