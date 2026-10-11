import pytest
from httpx import AsyncClient

DADOS_USUARIO = {
    "nome": "Matheus Rodrigues",
    "email": "matheus@example.com",
    "senha": "senha-segura-123",
}


@pytest.mark.anyio
async def test_cadastro_e_login(client_sem_auth: AsyncClient) -> None:
    cadastro = await client_sem_auth.post("/api/v1/auth/cadastro", json=DADOS_USUARIO)

    assert cadastro.status_code == 201
    assert cadastro.json()["email"] == "matheus@example.com"
    assert "senha" not in cadastro.json()
    assert "senha_hash" not in cadastro.json()

    login = await client_sem_auth.post(
        "/api/v1/auth/login",
        data={"username": "matheus@example.com", "password": "senha-segura-123"},
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


@pytest.mark.anyio
async def test_nao_permite_email_duplicado(client_sem_auth: AsyncClient) -> None:
    await client_sem_auth.post("/api/v1/auth/cadastro", json=DADOS_USUARIO)
    resposta = await client_sem_auth.post("/api/v1/auth/cadastro", json=DADOS_USUARIO)

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "EMAIL_DUPLICADO"


@pytest.mark.anyio
async def test_rejeita_login_invalido(client_sem_auth: AsyncClient) -> None:
    await client_sem_auth.post("/api/v1/auth/cadastro", json=DADOS_USUARIO)
    resposta = await client_sem_auth.post(
        "/api/v1/auth/login",
        data={"username": "matheus@example.com", "password": "senha-incorreta"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["erro"]["codigo"] == "NAO_AUTORIZADO"
    assert resposta.headers["www-authenticate"] == "Bearer"


@pytest.mark.anyio
async def test_protege_rotas_de_escrita(client_sem_auth: AsyncClient) -> None:
    sem_token = await client_sem_auth.post("/api/v1/categorias", json={"nome": "Limpeza"})
    token_invalido = await client_sem_auth.post(
        "/api/v1/categorias",
        json={"nome": "Limpeza"},
        headers={"Authorization": "Bearer token-invalido"},
    )
    consulta_publica = await client_sem_auth.get("/api/v1/categorias")

    assert sem_token.status_code == 401
    assert token_invalido.status_code == 401
    assert consulta_publica.status_code == 200
