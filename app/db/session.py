"""Engine do SQLAlchemy e sessão entregue às rotas por dependência."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# pool_pre_ping testa conexões reaproveitadas e troca as que foram encerradas pelo banco.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão à rota e a fecha quando a requisição termina.

    O ``yield`` permite que o FastAPI use a sessão durante o endpoint. Ao sair
    da requisição, o bloco ``with`` libera a conexão de volta para o pool.
    """

    with SessionLocal() as session:
        yield session
