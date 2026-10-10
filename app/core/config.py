from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecomp Stock API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ecomp_stock"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
