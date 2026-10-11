import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import ConflitoErro
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao
from app.models.produto import Produto
from app.schemas.movimentacao import MovimentacaoCriacao
from app.services.movimentacoes import criar_movimentacao

URL_POSTGRES_TESTE = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not URL_POSTGRES_TESTE,
    reason="Teste executado apenas quando há um PostgreSQL de teste.",
)


@pytest.fixture
def banco_postgres() -> sessionmaker[Session]:
    engine = create_engine(URL_POSTGRES_TESTE)
    SessaoPostgres = sessionmaker(bind=engine, expire_on_commit=False)

    with engine.begin() as conexao:
        conexao.execute(
            text(
                "TRUNCATE TABLE movimentacoes_estoque, produtos, fornecedores, categorias, "
                "usuarios "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield SessaoPostgres
    engine.dispose()


def test_duas_saidas_simultaneas_nao_deixam_estoque_negativo(
    banco_postgres: sessionmaker[Session],
) -> None:
    with banco_postgres() as db:
        categoria = Categoria(nome="Papelaria")
        fornecedor = Fornecedor(
            nome="Atacado Central",
            cnpj="12345678000190",
            telefone="75999999999",
            email="contato@atacadocentral.com.br",
        )
        db.add_all([categoria, fornecedor])
        db.flush()
        produto = Produto(
            nome="Caderno",
            sku="CAD-001",
            preco_custo="10.00",
            preco_venda="18.00",
            quantidade_estoque=1,
            estoque_minimo=0,
            categoria_id=categoria.id,
            fornecedor_id=fornecedor.id,
        )
        db.add(produto)
        db.commit()
        produto_id = produto.id

    barreira = Barrier(2)

    def registrar_saida() -> str:
        with banco_postgres() as db:
            barreira.wait()
            try:
                criar_movimentacao(
                    db,
                    MovimentacaoCriacao(
                        produto_id=produto_id,
                        tipo=TipoMovimentacao.SAIDA,
                        quantidade=1,
                    ),
                )
                return "registrada"
            except ConflitoErro as erro:
                return erro.codigo

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(lambda _: registrar_saida(), range(2)))

    with banco_postgres() as db:
        estoque = db.get(Produto, produto_id).quantidade_estoque
        total_movimentacoes = db.scalar(select(func.count()).select_from(MovimentacaoEstoque))

    assert sorted(resultados) == ["ESTOQUE_INSUFICIENTE", "registrada"]
    assert estoque == 0
    assert total_movimentacoes == 1
