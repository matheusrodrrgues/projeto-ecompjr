import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_de_categoria(client: AsyncClient) -> None:
    criacao = await client.post("/api/v1/categorias", json={"nome": "Eletronicos"})
    assert criacao.status_code == 201
    categoria_id = criacao.json()["id"]

    consulta = await client.get(f"/api/v1/categorias/{categoria_id}")
    assert consulta.status_code == 200
    assert consulta.json()["nome"] == "Eletronicos"

    atualizacao = await client.patch(
        f"/api/v1/categorias/{categoria_id}", json={"nome": "Informatica"}
    )
    assert atualizacao.status_code == 200
    assert atualizacao.json()["nome"] == "Informatica"

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
