# Ecomp Stock API

API para controlar produtos, fornecedores, categorias e entradas e saídas de estoque de uma loja de variedades.

## O que já funciona

- cadastro completo de categorias, fornecedores e produtos;
- busca de produtos por nome, categoria e fornecedor;
- consulta dos produtos com estoque baixo;
- registro de entrada e saída com atualização automática do saldo;
- histórico de movimentações com filtros por período, fornecedor, produto e tipo;
- erros no mesmo formato em toda a API;
- migrações do banco e testes automatizados.

## Como rodar

Tenha Docker e Docker Compose instalados. Depois, na pasta do projeto:

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api alembic upgrade head
```

A API fica em `http://localhost:8000`. Os links mais úteis são:

- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- saúde da API: `GET http://localhost:8000/health`

Para encerrar os containers, use `docker compose down`.

## Organização do projeto

- `app/api/routes`: recebe as requisições e chama os services;
- `app/models`: representa as tabelas e os relacionamentos do banco;
- `app/schemas`: valida os dados de entrada e define as respostas;
- `app/services`: concentra as consultas e regras de negócio;
- `alembic`: guarda o histórico de alterações do banco;
- `tests`: reúne os testes automatizados da API.

## Regras de estoque

Todo produto começa com estoque zero. O saldo não pode ser editado pela rota de produtos: ele só muda quando uma movimentação é registrada.

Uma entrada soma ao saldo e uma saída subtrai. Se não houver quantidade suficiente, a saída inteira é cancelada. O saldo e o histórico são gravados na mesma transação. Durante essa operação, o produto fica bloqueado no banco para evitar que duas saídas simultâneas usem o mesmo saldo.

As movimentações não possuem rotas de edição ou exclusão. Elas guardam o fornecedor que estava ligado ao produto no momento do registro, mantendo o histórico mesmo se o cadastro do produto mudar depois.

## Rotas

Todas as rotas de negócio usam o prefixo `/api/v1`.

| Método | Caminho | Uso |
| --- | --- | --- |
| POST, GET | `/categorias` | cadastrar e listar categorias |
| GET, PATCH, DELETE | `/categorias/{id}` | consultar, atualizar e excluir uma categoria |
| POST, GET | `/fornecedores` | cadastrar e listar fornecedores |
| GET, PATCH, DELETE | `/fornecedores/{id}` | consultar, atualizar e excluir um fornecedor |
| POST, GET | `/produtos` | cadastrar, listar e filtrar produtos |
| GET | `/produtos/estoque-baixo` | listar produtos no estoque mínimo ou abaixo dele |
| GET, PATCH, DELETE | `/produtos/{id}` | consultar, atualizar e excluir um produto |
| POST, GET | `/movimentacoes` | registrar ou listar movimentações |
| GET | `/movimentacoes/{id}` | consultar uma movimentação |

### Exemplo de entrada

```json
{
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 20,
  "observacao": "Compra do fornecedor"
}
```

Para uma saída, o corpo é o mesmo e o campo `tipo` recebe `saida`. A listagem aceita os parâmetros `data_inicio`, `data_fim`, `fornecedor_id`, `produto_id`, `tipo`, `offset` e `limite`.

Exemplo: `GET /api/v1/movimentacoes?data_inicio=2026-10-01&data_fim=2026-10-10&tipo=entrada`.

## Respostas de erro

Os erros seguem este formato:

```json
{
  "erro": {
    "codigo": "ESTOQUE_INSUFICIENTE",
    "mensagem": "O produto não possui estoque suficiente para essa saída."
  }
}
```

Os principais status usados são `400` para regra inválida, `404` para recurso não encontrado, `409` para conflito e `422` para campos inválidos.

## Testes e qualidade

Com o ambiente virtual ativo, execute:

```bash
pytest -q
ruff format --check .
ruff check .
```

Essas verificações também rodam no GitHub Actions a cada push ou pull request na branch `main`.

## Algumas decisões

- FastAPI foi usado pela validação dos dados e pela documentação Swagger pronta.
- SQLAlchemy concentra o acesso ao banco e Alembic controla as mudanças da estrutura.
- As regras ficam nos services para não misturar acesso ao banco com as rotas HTTP.
- Valores de dinheiro usam `Decimal` no lugar de `float`.
- Exclusões que quebrariam o histórico são recusadas.

## Uso de IA

Usei IA como apoio na estrutura inicial, na revisão das validações e na criação de alguns testes. As sugestões foram revisadas durante o desenvolvimento: os nomes do domínio foram mantidos em português, as mensagens de erro foram padronizadas e as regras de estoque ficaram separadas das rotas. Também revisei a atualização do saldo, o bloqueio usado nas movimentações e a preservação do histórico antes de manter essas partes no projeto.

