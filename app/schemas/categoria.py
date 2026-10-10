from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoriaBase(BaseModel):
    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome")
    @classmethod
    def limpar_nome(cls, nome: str) -> str:
        return nome.strip()


class CategoriaCriacao(CategoriaBase):
    pass


class CategoriaAtualizacao(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("nome")
    @classmethod
    def limpar_nome(cls, nome: str | None) -> str | None:
        return nome.strip() if nome is not None else None

    @model_validator(mode="after")
    def validar_alteracao(self) -> "CategoriaAtualizacao":
        if "nome" not in self.model_fields_set or self.nome is None:
            raise ValueError("Informe o nome que deseja atualizar.")
        return self


class CategoriaResposta(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
