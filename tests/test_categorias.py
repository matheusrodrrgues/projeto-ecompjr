import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_de_categoria(client: AsyncClient) -> None:
    criacao = await client.post("/api/v1/categorias", json={"nome": "Eletrônicos"})
    assert criacao.status_code == 201
    categoria_id = criacao.json()["id"]

    consulta = await client.get(f"/api/v1/categorias/{categoria_id}")
    assert consulta.status_code == 200
    assert consulta.json()["nome"] == "Eletrônicos"

    atualizacao = await client.patch(
        f"/api/v1/categorias/{categoria_id}", json={"nome": "Informática"}
    )
    assert atualizacao.status_code == 200
    assert atualizacao.json()["nome"] == "Informática"

    exclusao = await client.delete(f"/api/v1/categorias/{categoria_id}")
    assert exclusao.status_code == 204
    resposta_ausente = await client.get(f"/api/v1/categorias/{categoria_id}")
    assert resposta_ausente.status_code == 404


@pytest.mark.anyio
async def test_nao_permite_categoria_duplicada(client: AsyncClient) -> None:
    await client.post("/api/v1/categorias", json={"nome": "Limpeza"})
    resposta = await client.post("/api/v1/categorias", json={"nome": "Limpeza"})

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "CATEGORIA_DUPLICADA"


@pytest.mark.anyio
async def test_rejeita_nome_vazio_e_campo_desconhecido(client: AsyncClient) -> None:
    nome_vazio = await client.post("/api/v1/categorias", json={"nome": "   "})
    campo_desconhecido = await client.post(
        "/api/v1/categorias",
        json={"nome": "Limpeza", "ativo": True},
    )

    assert nome_vazio.status_code == 422
    assert campo_desconhecido.status_code == 422
