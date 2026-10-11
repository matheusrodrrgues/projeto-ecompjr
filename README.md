# Ecomp Stock API

API para controlar produtos, fornecedores, categorias e entradas e saídas de estoque de uma loja de variedades.

## O que já funciona

- cadastro completo de categorias, fornecedores e produtos;
- busca de produtos por nome, categoria e fornecedor;
- consulta dos produtos com estoque baixo;
- registro de entrada e saída com atualização automática do saldo;
- histórico de movimentações com filtros por período, fornecedor, produto e tipo;
- cadastro e login de usuários com autenticação JWT;
- proteção das rotas que alteram os dados;
- erros no mesmo formato em toda a API;
- migrações do banco e testes automatizados.

## Como rodar

Tenha Docker e Docker Compose instalados. Depois, na pasta do projeto:

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api alembic upgrade head
```

No PowerShell, use `Copy-Item .env.example .env` no lugar do primeiro comando.

A API fica em `http://localhost:8000`. Os links mais úteis são:

- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- saúde da API: `GET http://localhost:8000/health`

Para encerrar os containers, use `docker compose down`.

As configurações ficam no `.env`:

| Variável | Uso |
| --- | --- |
| `APP_NAME` | nome exibido no Swagger |
| `DATABASE_URL` | conexão com o PostgreSQL |
| `JWT_SECRET` | chave de assinatura dos tokens; mínimo de 32 caracteres |
| `JWT_EXPIRACAO_MINUTOS` | tempo de validade do token |

## Organização do projeto

- `app/api/routes`: recebe as requisições e chama os services;
- `app/models`: representa as tabelas e os relacionamentos do banco;
- `app/schemas`: valida os dados de entrada e define as respostas;
- `app/services`: concentra as consultas e regras de negócio;
- `alembic`: guarda o histórico de alterações do banco;
- `tests`: reúne os testes automatizados da API.

O caminho normal de uma requisição é: rota recebe e valida os dados, service executa a regra de negócio e model lê ou grava no banco. Essa separação evita colocar regra de estoque dentro dos endpoints.

## Modelagem

| Entidade | Campos principais | Regras |
| --- | --- | --- |
| Categoria | nome | nome único |
| Fornecedor | nome, CNPJ, telefone e e-mail | CNPJ e e-mail únicos |
| Produto | nome, SKU, preços, estoque mínimo, categoria e fornecedor | SKU único; estoque começa em zero |
| Movimentação | produto, fornecedor, tipo, quantidade, data e observação | somente criação e consulta |
| Usuário | nome, e-mail e hash da senha | e-mail único; senha não é salva em texto |

## Autenticação

As consultas são públicas. Para cadastrar, alterar ou excluir dados e registrar movimentações, é preciso estar autenticado.

Primeiro, crie um usuário em `POST /api/v1/auth/cadastro`:

```json
{
  "nome": "Matheus Rodrigues",
  "email": "matheus@example.com",
  "senha": "senha-segura-123"
}
```

Depois, faça login em `POST /api/v1/auth/login`. Essa rota recebe dados de formulário: informe o e-mail no campo `username` e a senha no campo `password`. A resposta contém o token JWT.

No Swagger, clique em **Authorize** e use o mesmo e-mail e senha. Fora do Swagger, envie o token no cabeçalho `Authorization`:

```text
Authorization: Bearer seu-token
```

A senha nunca é devolvida pela API e é salva no banco somente depois de passar pelo hash Argon2. A chave usada para assinar os tokens fica na variável `JWT_SECRET` do arquivo `.env` e deve ter pelo menos 32 caracteres.

### Teste rápido pelo Swagger

1. Abra `http://localhost:8000/docs`.
2. Use `POST /api/v1/auth/cadastro` para criar um usuário.
3. Clique em **Authorize** e informe o e-mail no campo `username` e a senha.
4. Cadastre uma categoria e um fornecedor.
5. Cadastre um produto usando os IDs criados.
6. Registre uma entrada e confira o saldo em `GET /api/v1/produtos/{produto_id}`.
7. Registre uma saída e consulte o histórico em `GET /api/v1/movimentacoes`.

## Regras de estoque

Todo produto começa com estoque zero. O saldo não pode ser editado pela rota de produtos: ele só muda quando uma movimentação é registrada.

Uma entrada soma ao saldo e uma saída subtrai. Se não houver quantidade suficiente, a saída inteira é cancelada. O saldo e o histórico são gravados na mesma transação. Durante essa operação, o produto fica bloqueado no banco para evitar que duas saídas simultâneas usem o mesmo saldo.

As movimentações não possuem rotas de edição ou exclusão. Elas guardam o fornecedor que estava ligado ao produto no momento do registro, mantendo o histórico mesmo se o cadastro do produto mudar depois.

## Rotas e respostas

Todas as rotas de negócio usam o prefixo `/api/v1`.

| Método | Caminho | Autenticação | Sucesso | Erros esperados |
| --- | --- | --- | --- | --- |
| POST | `/auth/cadastro` | não | `201` usuário criado | `409` e-mail repetido; `422` dados inválidos |
| POST | `/auth/login` | não | `200` token JWT | `401` credenciais inválidas; `422` formulário inválido |
| POST | `/categorias` | sim | `201` categoria criada | `409` nome repetido; `422` dados inválidos |
| GET | `/categorias` | não | `200` lista paginada | `422` paginação inválida |
| GET | `/categorias/{categoria_id}` | não | `200` categoria | `404` não encontrada |
| PATCH | `/categorias/{categoria_id}` | sim | `200` categoria alterada | `404`, `409` ou `422` |
| DELETE | `/categorias/{categoria_id}` | sim | `204` sem corpo | `404` ou `409` se possuir produtos |
| POST | `/fornecedores` | sim | `201` fornecedor criado | `409` CNPJ/e-mail repetido; `422` dados inválidos |
| GET | `/fornecedores` | não | `200` lista paginada | `422` paginação inválida |
| GET | `/fornecedores/{fornecedor_id}` | não | `200` fornecedor | `404` não encontrado |
| PATCH | `/fornecedores/{fornecedor_id}` | sim | `200` fornecedor alterado | `404`, `409` ou `422` |
| DELETE | `/fornecedores/{fornecedor_id}` | sim | `204` sem corpo | `404` ou `409` se estiver em uso ou no histórico |
| POST | `/produtos` | sim | `201` produto criado | `404` relação inexistente; `409` SKU repetido; `422` dados inválidos |
| GET | `/produtos` | não | `200` lista filtrada | `422` filtro inválido |
| GET | `/produtos/estoque-baixo` | não | `200` produtos no mínimo ou abaixo dele | `422` paginação inválida |
| GET | `/produtos/{produto_id}` | não | `200` produto | `404` não encontrado |
| PATCH | `/produtos/{produto_id}` | sim | `200` produto alterado | `404`, `409` ou `422` |
| DELETE | `/produtos/{produto_id}` | sim | `204` sem corpo | `404` ou `409` se possuir movimentações |
| POST | `/movimentacoes` | sim | `201` movimentação criada | `404` produto inexistente; `409` estoque insuficiente; `422` dados inválidos |
| GET | `/movimentacoes` | não | `200` histórico filtrado | `400` período invertido; `422` filtro inválido |
| GET | `/movimentacoes/{movimentacao_id}` | não | `200` movimentação | `404` não encontrada |

As listagens usam `offset` a partir de zero e `limite` entre 1 e 100. Produtos podem ser filtrados por `nome`, `categoria_id` e `fornecedor_id`. Movimentações aceitam `data_inicio`, `data_fim`, `fornecedor_id`, `produto_id` e `tipo` (`entrada` ou `saida`).

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

Os principais status usados são `400` para regra inválida, `401` para autenticação ausente ou inválida, `404` para recurso não encontrado, `409` para conflito e `422` para campos inválidos.

Erros inesperados retornam `500` com uma mensagem genérica. O detalhe técnico é enviado apenas para o log da aplicação, sem expor stack trace ao cliente.

## Testes e qualidade

Com o ambiente virtual ativo, execute:

```bash
pytest -q
ruff format --check .
ruff check .
```

Essas verificações também rodam no GitHub Actions a cada push ou pull request na branch `main`. O workflow inicia um PostgreSQL, aplica as migrations e testa duas saídas simultâneas para conferir o bloqueio do estoque.

O arquivo [docs/DEFESA.md](docs/DEFESA.md) reúne os pontos principais para revisar antes da apresentação.

## Algumas decisões

- FastAPI foi usado pela validação dos dados e pela documentação Swagger pronta.
- SQLAlchemy concentra o acesso ao banco e Alembic controla as mudanças da estrutura.
- As regras ficam nos services para não misturar acesso ao banco com as rotas HTTP.
- Senhas usam hash Argon2 e os tokens JWT expiram após o tempo definido no `.env`.
- Valores de dinheiro usam `Decimal` no lugar de `float`.
- Exclusões que quebrariam o histórico são recusadas.

## Uso de IA

Usei IA como apoio na estrutura inicial, na revisão das validações e na criação de alguns testes. As sugestões foram revisadas durante o desenvolvimento: os nomes do domínio foram mantidos em português, as mensagens de erro foram padronizadas e as regras de estoque ficaram separadas das rotas. Também revisei a atualização do saldo, o bloqueio usado nas movimentações e a preservação do histórico antes de manter essas partes no projeto.

