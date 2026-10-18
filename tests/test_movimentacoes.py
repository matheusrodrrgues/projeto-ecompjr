import pytest
from httpx import AsyncClient


async def criar_produto(client: AsyncClient) -> tuple[int, int]:
    categoria = await client.post("/api/v1/categorias", json={"nome": "Papelaria"})
    fornecedor = await client.post(
        "/api/v1/fornecedores",
        json={
            "nome": "Atacado Central",
            "cnpj": "12.345.678/0001-90",
            "telefone": "75999999999",
            "email": "contato@atacadocentral.com.br",
        },
    )
    produto = await client.post(
        "/api/v1/produtos",
        json={
            "nome": "Caderno",
            "sku": "CAD-001",
            "preco_custo": "10.00",
            "preco_venda": "18.00",
            "estoque_minimo": 5,
            "categoria_id": categoria.json()["id"],
            "fornecedor_id": fornecedor.json()["id"],
        },
    )
    return produto.json()["id"], fornecedor.json()["id"]


@pytest.mark.anyio
async def test_entrada_e_saida_atualizam_estoque(
    client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO", logger="app.services.movimentacoes")
    produto_id, fornecedor_id = await criar_produto(client)

    entrada = await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 10},
    )
    saida = await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "saida", "quantidade": 4},
    )
    produto = await client.get(f"/api/v1/produtos/{produto_id}")

    assert entrada.status_code == 201
    assert entrada.json()["fornecedor_id"] == fornecedor_id
    assert saida.status_code == 201
    assert produto.json()["quantidade_estoque"] == 6
    assert (
        sum(registro.message.startswith("movimentacao_criada") for registro in caplog.records) == 2
    )


@pytest.mark.anyio
async def test_saida_sem_estoque_nao_e_registrada(
    client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("WARNING", logger="app.services.movimentacoes")
    produto_id, _ = await criar_produto(client)

    resposta = await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "saida", "quantidade": 1},
    )
    produto = await client.get(f"/api/v1/produtos/{produto_id}")
    movimentacoes = await client.get("/api/v1/movimentacoes")

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "ESTOQUE_INSUFICIENTE"
    assert produto.json()["quantidade_estoque"] == 0
    assert movimentacoes.json() == []
    assert any(registro.message.startswith("estoque_insuficiente") for registro in caplog.records)


@pytest.mark.anyio
async def test_lista_movimentacoes_com_filtros(client: AsyncClient) -> None:
    produto_id, fornecedor_id = await criar_produto(client)
    movimentacao = await client.post(
        "/api/v1/movimentacoes",
        json={
            "produto_id": produto_id,
            "tipo": "entrada",
            "quantidade": 8,
            "observacao": "  compra inicial  ",
        },
    )
    data_movimentacao = movimentacao.json()["data"][:10]

    resposta = await client.get(
        "/api/v1/movimentacoes",
        params={
            "data_inicio": data_movimentacao,
            "data_fim": data_movimentacao,
            "fornecedor_id": fornecedor_id,
            "produto_id": produto_id,
            "tipo": "entrada",
        },
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["observacao"] == "compra inicial"


@pytest.mark.anyio
async def test_rejeita_periodo_invertido(client: AsyncClient) -> None:
    resposta = await client.get(
        "/api/v1/movimentacoes",
        params={"data_inicio": "2026-10-10", "data_fim": "2026-10-09"},
    )

    assert resposta.status_code == 400
    assert resposta.json()["erro"]["codigo"] == "PERIODO_INVALIDO"


@pytest.mark.anyio
async def test_movimentacao_nao_pode_ser_alterada_ou_excluida(client: AsyncClient) -> None:
    produto_id, _ = await criar_produto(client)
    criacao = await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 5},
    )
    movimentacao_id = criacao.json()["id"]

    alteracao = await client.patch(
        f"/api/v1/movimentacoes/{movimentacao_id}", json={"quantidade": 20}
    )
    exclusao = await client.delete(f"/api/v1/movimentacoes/{movimentacao_id}")

    assert alteracao.status_code == 405
    assert alteracao.json()["erro"]["mensagem"] == "Método não permitido."
    assert exclusao.status_code == 405


@pytest.mark.anyio
async def test_produto_com_movimentacao_nao_pode_ser_excluido(client: AsyncClient) -> None:
    produto_id, _ = await criar_produto(client)
    await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 5},
    )

    resposta = await client.delete(f"/api/v1/produtos/{produto_id}")

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "PRODUTO_COM_HISTORICO"


@pytest.mark.anyio
async def test_fornecedor_do_historico_nao_pode_ser_excluido(client: AsyncClient) -> None:
    produto_id, fornecedor_antigo_id = await criar_produto(client)
    await client.post(
        "/api/v1/movimentacoes",
        json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 5},
    )
    novo_fornecedor = await client.post(
        "/api/v1/fornecedores",
        json={
            "nome": "Novo Atacado",
            "cnpj": "98.765.432/0001-10",
            "telefone": "7533334444",
            "email": "contato@novoatacado.com.br",
        },
    )
    await client.patch(
        f"/api/v1/produtos/{produto_id}",
        json={"fornecedor_id": novo_fornecedor.json()["id"]},
    )

    resposta = await client.delete(f"/api/v1/fornecedores/{fornecedor_antigo_id}")

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "FORNECEDOR_COM_HISTORICO"
