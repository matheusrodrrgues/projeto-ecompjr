from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    produtos: Mapped[list["Produto"]] = relationship(back_populates="fornecedor")

