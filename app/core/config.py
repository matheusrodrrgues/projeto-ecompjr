"""Leitura das configurações definidas no ambiente ou no arquivo .env."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações necessárias para iniciar a aplicação."""

    app_name: str = "jrEstoqueAPI"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ecomp_stock"
    jwt_secret: str = Field(min_length=32)
    jwt_expiracao_minutos: int = Field(default=60, gt=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
