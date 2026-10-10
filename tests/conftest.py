from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessaoTeste = sessionmaker(bind=engine_teste, expire_on_commit=False)


@event.listens_for(engine_teste, "connect")
def ativar_chaves_estrangeiras(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db() -> Session:
    Base.metadata.create_all(engine_teste)
    with SessaoTeste() as session:
        yield session
    Base.metadata.drop_all(engine_teste)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(db: Session) -> AsyncIterator[AsyncClient]:
    def sobrescrever_banco():
        yield db

    app.dependency_overrides[get_db] = sobrescrever_banco
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
