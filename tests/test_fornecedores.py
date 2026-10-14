import pytest
from httpx import AsyncClient

DADOS_FORNECEDOR = {
    "nome": "Distribuidora Feira",
    "cnpj": "12.345.678/0001-90",
    "telefone": "75999999999",
    "email": "contato@distribuidorafeira.com.br",
}


@pytest.mark.anyio
async def test_crud_de_fornecedor(client: AsyncClient) -> None:
    criacao = await client.post("/api/v1/fornecedores", json=DADOS_FORNECEDOR)
    assert criacao.status_code == 201
    fornecedor_id = criacao.json()["id"]
    assert criacao.json()["cnpj"] == "12345678000190"

    consulta = await client.get(f"/api/v1/fornecedores/{fornecedor_id}")
    assert consulta.status_code == 200

    atualizacao = await client.patch(
        f"/api/v1/fornecedores/{fornecedor_id}",
        json={
            "telefone": "7533334444",
            "email": "Novo@DistribuidoraFeira.com.br",
        },
    )
    assert atualizacao.status_code == 200
    assert atualizacao.json()["telefone"] == "7533334444"
    assert atualizacao.json()["email"] == "novo@distribuidorafeira.com.br"

    exclusao = await client.delete(f"/api/v1/fornecedores/{fornecedor_id}")
    assert exclusao.status_code == 204


@pytest.mark.anyio
async def test_nao_permite_cnpj_duplicado(client: AsyncClient) -> None:
    await client.post("/api/v1/fornecedores", json=DADOS_FORNECEDOR)
    duplicado = {**DADOS_FORNECEDOR, "email": "outro@email.com"}
    resposta = await client.post("/api/v1/fornecedores", json=duplicado)

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "CNPJ_DUPLICADO"


@pytest.mark.anyio
async def test_valida_formato_do_cnpj(client: AsyncClient) -> None:
    dados = {**DADOS_FORNECEDOR, "cnpj": "123"}
    resposta = await client.post("/api/v1/fornecedores", json=dados)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "DADOS_INVALIDOS"


@pytest.mark.anyio
async def test_rejeita_cnpj_enviado_com_tipo_invalido(client: AsyncClient) -> None:
    dados = {**DADOS_FORNECEDOR, "cnpj": 12345678000190}
    resposta = await client.post("/api/v1/fornecedores", json=dados)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "DADOS_INVALIDOS"


@pytest.mark.anyio
async def test_email_duplicado_ignora_maiusculas_e_minusculas(client: AsyncClient) -> None:
    primeiro = {**DADOS_FORNECEDOR, "email": "Contato@DistribuidoraFeira.com.br"}
    await client.post("/api/v1/fornecedores", json=primeiro)

    duplicado = {
        **DADOS_FORNECEDOR,
        "cnpj": "98.765.432/0001-10",
        "email": "contato@distribuidorafeira.com.br",
    }
    resposta = await client.post("/api/v1/fornecedores", json=duplicado)

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "EMAIL_DUPLICADO"


@pytest.mark.anyio
async def test_rejeita_campo_desconhecido(client: AsyncClient) -> None:
    dados = {**DADOS_FORNECEDOR, "site": "https://exemplo.com"}
    resposta = await client.post("/api/v1/fornecedores", json=dados)

    assert resposta.status_code == 422
