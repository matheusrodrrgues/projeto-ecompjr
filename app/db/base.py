"""Base comum de todos os models do SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Permite que o Alembic encontre os metadados das tabelas."""
