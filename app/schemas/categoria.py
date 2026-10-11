from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoriaBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome", mode="before")
    @classmethod
    def limpar_nome(cls, nome: str) -> str:
        return nome.strip() if isinstance(nome, str) else nome


class CategoriaCriacao(CategoriaBase):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"nome": "Papelaria"}]},
    )


class CategoriaAtualizacao(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"nome": "Material escolar"}]},
    )

    nome: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("nome", mode="before")
    @classmethod
    def limpar_nome(cls, nome: str | None) -> str | None:
        return nome.strip() if isinstance(nome, str) else nome

    @model_validator(mode="after")
    def validar_alteracao(self) -> "CategoriaAtualizacao":
        if "nome" not in self.model_fields_set or self.nome is None:
            raise ValueError("Informe o nome que deseja atualizar.")
        return self


class CategoriaResposta(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
