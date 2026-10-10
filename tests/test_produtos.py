from decimal import Decimal

import pytest
from httpx import AsyncClient


async def criar_relacionamentos(client: AsyncClient) -> tuple[int, int]:
    categoria = await client.post("/api/v1/categorias", json={"nome": "Eletronicos"})
    fornecedor = await client.post(
        "/api/v1/fornecedores",
        json={
            "nome": "Distribuidora Feira",
            "cnpj": "12.345.678/0001-90",
            "telefone": "75999999999",
            "email": "contato@distribuidorafeira.com.br",
        },
    )
    return categoria.json()["id"], fornecedor.json()["id"]


def dados_produto(categoria_id: int, fornecedor_id: int) -> dict:
    return {
        "nome": "Teclado Mecanico",
        "sku": "tec-001",
        "preco_custo": "120.00",
        "preco_venda": "199.90",
        "estoque_minimo": 5,
        "categoria_id": categoria_id,
        "fornecedor_id": fornecedor_id,
    }


@pytest.mark.anyio
async def test_crud_de_produto(client: AsyncClient) -> None:
    categoria_id, fornecedor_id = await criar_relacionamentos(client)
    criacao = await client.post("/api/v1/produtos", json=dados_produto(categoria_id, fornecedor_id))

    assert criacao.status_code == 201
    produto_id = criacao.json()["id"]
    assert criacao.json()["sku"] == "TEC-001"
    assert criacao.json()["quantidade_estoque"] == 0

    consulta = await client.get(f"/api/v1/produtos/{produto_id}")
    assert consulta.status_code == 200

    atualizacao = await client.patch(
        f"/api/v1/produtos/{produto_id}", json={"preco_venda": "189.90"}
    )
    assert atualizacao.status_code == 200
    assert Decimal(atualizacao.json()["preco_venda"]) == Decimal("189.90")

    exclusao = await client.delete(f"/api/v1/produtos/{produto_id}")
    assert exclusao.status_code == 204


@pytest.mark.anyio
async def test_nao_permite_sku_duplicado(client: AsyncClient) -> None:
    categoria_id, fornecedor_id = await criar_relacionamentos(client)
    dados = dados_produto(categoria_id, fornecedor_id)
    await client.post("/api/v1/produtos", json=dados)
    resposta = await client.post("/api/v1/produtos", json=dados)

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "SKU_DUPLICADO"


@pytest.mark.anyio
async def test_exige_categoria_e_fornecedor_existentes(client: AsyncClient) -> None:
    dados = dados_produto(categoria_id=999, fornecedor_id=999)
    resposta = await client.post("/api/v1/produtos", json=dados)

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["mensagem"] == "Recurso nao encontrado: Categoria."


@pytest.mark.anyio
async def test_nao_aceita_alteracao_direta_do_estoque(client: AsyncClient) -> None:
    categoria_id, fornecedor_id = await criar_relacionamentos(client)
    dados = dados_produto(categoria_id, fornecedor_id)
    dados["quantidade_estoque"] = 20

    resposta = await client.post("/api/v1/produtos", json=dados)

    assert resposta.status_code == 422


@pytest.mark.anyio
async def test_lista_produtos_com_estoque_baixo_e_filtros(client: AsyncClient) -> None:
    categoria_id, fornecedor_id = await criar_relacionamentos(client)
    await client.post("/api/v1/produtos", json=dados_produto(categoria_id, fornecedor_id))

    estoque_baixo = await client.get("/api/v1/produtos/estoque-baixo")
    assert estoque_baixo.status_code == 200
    assert len(estoque_baixo.json()) == 1

    filtrados = await client.get(
        "/api/v1/produtos",
        params={"nome": "teclado", "categoria_id": categoria_id},
    )
    assert filtrados.status_code == 200
    assert len(filtrados.json()) == 1

    sem_resultado = await client.get("/api/v1/produtos", params={"nome": "mouse"})
    assert sem_resultado.status_code == 200
    assert sem_resultado.json() == []
