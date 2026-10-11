from app.main import app


def test_openapi_tem_informacoes_e_exemplos() -> None:
    openapi = app.openapi()

    assert openapi["info"]["title"] == "jrEstoqueAPI"
    assert openapi["info"]["version"] == "1.0.0"
    assert openapi["components"]["schemas"]["ProdutoCriacao"]["examples"]
    assert openapi["components"]["schemas"]["MovimentacaoCriacao"]["examples"]


def test_openapi_marca_rotas_protegidas() -> None:
    openapi = app.openapi()

    criacao = openapi["paths"]["/api/v1/produtos"]["post"]
    consulta = openapi["paths"]["/api/v1/produtos"]["get"]

    assert criacao["security"] == [{"OAuth2PasswordBearer": []}]
    assert "security" not in consulta
    assert criacao["summary"] == "Cadastrar produto"
    assert set(criacao["responses"]) == {"201", "401", "404", "409", "422", "500"}
    exemplo_erro = criacao["responses"]["422"]["content"]["application/json"]["example"]
    assert exemplo_erro["erro"]["codigo"] == "DADOS_INVALIDOS"
