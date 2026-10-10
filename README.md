# Ecomp Stock API

API para controlar produtos, fornecedores, categorias e entradas e saidas de estoque de uma loja de variedades.

## O que ja funciona

- cadastro completo de categorias, fornecedores e produtos;
- busca de produtos por nome, categoria e fornecedor;
- consulta dos produtos com estoque baixo;
- registro de entrada e saida com atualizacao automatica do saldo;
- historico de movimentacoes com filtros por periodo, fornecedor, produto e tipo;
- erros no mesmo formato em toda a API;
- migrations do banco e testes automatizados.

## Como rodar

Tenha Docker e Docker Compose instalados. Depois, na pasta do projeto:

```bash
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
```

A API fica em `http://localhost:8000`. Os links mais uteis sao:

- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- saude da API: `GET http://localhost:8000/health`

## Regras de estoque

Todo produto comeca com estoque zero. O saldo nao pode ser editado pela rota de produtos: ele so muda quando uma movimentacao e registrada.

Uma entrada soma ao saldo e uma saida subtrai. Se nao houver quantidade suficiente, a saida inteira e cancelada. O saldo e o historico sao gravados na mesma transacao. Durante essa operacao, o produto fica bloqueado no banco para evitar que duas saidas simultaneas usem o mesmo saldo.

As movimentacoes nao possuem rotas de edicao ou exclusao. Elas guardam o fornecedor que estava ligado ao produto no momento do registro, mantendo o historico mesmo se o cadastro do produto mudar depois.

## Rotas

Todas as rotas de negocio usam o prefixo `/api/v1`.

| Metodo | Caminho | Uso |
| --- | --- | --- |
| POST, GET | `/categorias` | cadastrar e listar categorias |
| GET, PATCH, DELETE | `/categorias/{id}` | consultar, atualizar e excluir uma categoria |
| POST, GET | `/fornecedores` | cadastrar e listar fornecedores |
| GET, PATCH, DELETE | `/fornecedores/{id}` | consultar, atualizar e excluir um fornecedor |
| POST, GET | `/produtos` | cadastrar, listar e filtrar produtos |
| GET | `/produtos/estoque-baixo` | listar produtos no estoque minimo ou abaixo dele |
| GET, PATCH, DELETE | `/produtos/{id}` | consultar, atualizar e excluir um produto |
| POST, GET | `/movimentacoes` | registrar ou listar movimentacoes |
| GET | `/movimentacoes/{id}` | consultar uma movimentacao |

### Exemplo de entrada

```json
{
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 20,
  "observacao": "Compra do fornecedor"
}
```

Para uma saida, o corpo e o mesmo e o campo `tipo` recebe `saida`. A listagem aceita os parametros `data_inicio`, `data_fim`, `fornecedor_id`, `produto_id`, `tipo`, `offset` e `limite`.

Exemplo: `GET /api/v1/movimentacoes?data_inicio=2026-10-01&data_fim=2026-10-10&tipo=entrada`.

## Respostas de erro

Os erros seguem este formato:

```json
{
  "erro": {
    "codigo": "ESTOQUE_INSUFICIENTE",
    "mensagem": "O produto nao possui estoque suficiente para essa saida."
  }
}
```

Os principais status usados sao `400` para regra invalida, `404` para recurso nao encontrado, `409` para conflito e `422` para campos invalidos.

## Testes e qualidade

Com o ambiente virtual ativo, execute:

```bash
pytest -q
ruff format --check .
ruff check .
```

Essas verificacoes tambem rodam no GitHub Actions a cada push ou pull request na branch `main`.

## Algumas decisoes

- FastAPI foi usado pela validacao dos dados e pela documentacao Swagger pronta.
- SQLAlchemy concentra o acesso ao banco e Alembic controla as mudancas da estrutura.
- As regras ficam nos services para nao misturar acesso ao banco com as rotas HTTP.
- Valores de dinheiro usam `Decimal` no lugar de `float`.
- Exclusoes que quebrariam o historico sao recusadas.

## Uso de IA

IA foi usada como apoio para organizar a estrutura, revisar regras e investigar erros. O codigo foi ajustado ao enunciado e cada decisao importante ficou registrada neste README.

