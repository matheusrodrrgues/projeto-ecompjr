# jrEstoqueAPI

API REST desenvolvida para organizar o estoque de uma loja de variedades. O projeto reúne o
cadastro de produtos, fornecedores e categorias, além de registrar todas as entradas e saídas de
estoque para manter um histórico confiável das operações.

Esta aplicação foi criada para o desafio técnico da trilha de Back-end da Ecomp Jr. O objetivo foi
resolver primeiro o fluxo principal do negócio e, depois, acrescentar autenticação, testes
automatizados e proteção contra alterações simultâneas no estoque.

## Visão geral

O controle manual de estoque dificulta saber quais produtos estão disponíveis, quem os fornece e
como o saldo mudou ao longo do tempo. A API centraliza essas informações e aplica regras para que
os dados permaneçam consistentes.

Principais funcionalidades:

- CRUD de categorias, fornecedores e produtos;
- registro imutável de entradas e saídas de estoque;
- atualização automática do saldo a cada movimentação;
- busca de produtos por nome, categoria e fornecedor;
- consulta de produtos com estoque mínimo ou abaixo dele;
- filtros do histórico por período, fornecedor, produto e tipo;
- respostas de erro padronizadas, sem exposição de stack trace;
- cadastro e login de usuários com JWT;
- testes automatizados e validação contínua com GitHub Actions;
- bloqueio do produto durante a movimentação para evitar condições de corrida.

## Documentação interativa

O FastAPI gera a documentação OpenAPI da aplicação. Com o projeto rodando, o Swagger fica
disponível em `http://localhost:8000/docs` e permite consultar e testar todas as rotas.

![Documentação da API no Swagger](docs/imagens/swagger-api.jpg)

Também é possível acessar o JSON do OpenAPI em `http://localhost:8000/openapi.json`.

## Tecnologias utilizadas

- Python 3.12;
- FastAPI;
- PostgreSQL 17;
- SQLAlchemy 2;
- Alembic;
- Pydantic;
- PyJWT e Argon2;
- Pytest e HTTPX;
- Ruff;
- Docker e Docker Compose;
- GitHub Actions.

## Como executar

### Pré-requisitos

- Docker com Docker Compose;
- Git, caso o projeto ainda precise ser clonado.

### 1. Preparar as variáveis de ambiente

Na raiz do projeto, copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Antes de usar a aplicação fora de um ambiente local, troque o valor de `JWT_SECRET` por uma chave
longa e aleatória.

### 2. Subir a API e o PostgreSQL

```bash
docker compose up --build -d
```

O Compose aguarda o PostgreSQL ficar saudável antes de iniciar a API.

### 3. Aplicar as migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Conferir se a API está funcionando

Abra `http://localhost:8000/docs` ou faça a verificação:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

Para acompanhar os logs:

```bash
docker compose logs -f api
```

Para encerrar os containers:

```bash
docker compose down
```

Os dados do PostgreSQL ficam preservados no volume `postgres_data`. Para também remover esse
volume, use `docker compose down -v`.

## Variáveis de ambiente

| Variável | Descrição | Exemplo |
| --- | --- | --- |
| `APP_NAME` | Nome exibido na documentação da API | `jrEstoqueAPI` |
| `DATABASE_URL` | Endereço de conexão usado pelo SQLAlchemy | `postgresql+psycopg://postgres:postgres@db:5432/ecomp_stock` |
| `JWT_SECRET` | Chave usada para assinar os tokens, com no mínimo 32 caracteres | definida no `.env` |
| `JWT_EXPIRACAO_MINUTOS` | Tempo de validade do token | `60` |

O arquivo `.env` não é versionado. O `.env.example` contém apenas valores próprios para o ambiente
local.

## Organização do projeto

```text
ecomp-stock-api/
├── .github/workflows/    # pipeline de formatação, lint, migrations e testes
├── alembic/              # histórico de alterações do banco
├── app/
│   ├── api/              # rotas HTTP, autenticação das rotas e exemplos OpenAPI
│   ├── core/             # configurações, segurança e exceções da aplicação
│   ├── db/               # conexão, sessões e base do SQLAlchemy
│   ├── models/           # tabelas e relacionamentos do banco
│   ├── schemas/          # validação das entradas e formato das respostas
│   ├── services/         # regras de negócio e operações no banco
│   └── main.py           # criação da aplicação e tratamento global de erros
├── docs/                 # material de apoio para a defesa e imagens
├── tests/                # testes dos endpoints e das regras de negócio
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

O fluxo mais comum é:

```text
requisição -> rota -> schema -> service -> model -> PostgreSQL
```

A rota recebe a requisição e declara o contrato HTTP. O schema valida os dados. O service aplica a
regra de negócio e usa os models para consultar ou alterar o banco. Essa separação mantém as rotas
menores e permite testar as regras sem duplicá-las.

## Modelagem e relacionamentos

| Entidade | Campos principais | Regras |
| --- | --- | --- |
| Categoria | `id`, `nome`, `criado_em` | nome único |
| Fornecedor | `id`, `nome`, `cnpj`, `telefone`, `email`, `criado_em` | CNPJ e e-mail únicos |
| Produto | `id`, `nome`, `sku`, preços, saldo, estoque mínimo e vínculos | SKU único; saldo inicial igual a zero |
| Movimentação | produto, fornecedor, tipo, quantidade, data e observação | somente criação e consulta |
| Usuário | `id`, `nome`, `email`, `senha_hash`, `criado_em` | e-mail único; senha armazenada como hash |

Cada produto pertence a uma categoria e a um fornecedor. As chaves estrangeiras usam restrição de
exclusão: um cadastro em uso não pode ser removido e deixar referências quebradas.

A movimentação guarda tanto o produto quanto o fornecedor ligado a ele no momento da operação.
Assim, se o produto mudar de fornecedor depois, o histórico antigo continua representando o que
realmente aconteceu.

## Autenticação

As consultas são públicas. As operações que criam, alteram ou excluem dados exigem autenticação.

### Cadastro

`POST /api/v1/auth/cadastro`

```json
{
  "nome": "Matheus Rodrigues",
  "email": "matheus@example.com",
  "senha": "senha-segura-123"
}
```

A senha passa pelo Argon2 antes de ser salva. A API nunca devolve a senha nem seu hash.

### Login

`POST /api/v1/auth/login` recebe `application/x-www-form-urlencoded`:

```text
username=matheus@example.com
password=senha-segura-123
```

O campo se chama `username` porque esse é o formato esperado pelo OAuth2, mas seu valor é o e-mail
do usuário. Em caso de sucesso, a resposta é:

```json
{
  "access_token": "token-jwt",
  "token_type": "bearer"
}
```

No Swagger, basta clicar em **Authorize** e informar o mesmo e-mail e senha. Em outro cliente HTTP,
envie o token no cabeçalho:

```text
Authorization: Bearer token-jwt
```

## Endpoints

Todas as rotas de negócio usam o prefixo `/api/v1`.

| Método | Rota | Auth | Descrição | Sucesso | Erros previstos |
| --- | --- | --- | --- | --- | --- |
| `POST` | `/auth/cadastro` | não | cadastra um usuário | `201` | `409`, `422`, `500` |
| `POST` | `/auth/login` | não | valida as credenciais e gera um JWT | `200` | `401`, `422`, `500` |
| `POST` | `/categorias` | sim | cadastra uma categoria | `201` | `401`, `409`, `422`, `500` |
| `GET` | `/categorias` | não | lista categorias com paginação | `200` | `422`, `500` |
| `GET` | `/categorias/{categoria_id}` | não | busca uma categoria | `200` | `404`, `422`, `500` |
| `PATCH` | `/categorias/{categoria_id}` | sim | altera o nome de uma categoria | `200` | `401`, `404`, `409`, `422`, `500` |
| `DELETE` | `/categorias/{categoria_id}` | sim | exclui uma categoria sem produtos | `204` | `401`, `404`, `409`, `422`, `500` |
| `POST` | `/fornecedores` | sim | cadastra um fornecedor | `201` | `401`, `409`, `422`, `500` |
| `GET` | `/fornecedores` | não | lista fornecedores com paginação | `200` | `422`, `500` |
| `GET` | `/fornecedores/{fornecedor_id}` | não | busca um fornecedor | `200` | `404`, `422`, `500` |
| `PATCH` | `/fornecedores/{fornecedor_id}` | sim | altera os campos enviados | `200` | `401`, `404`, `409`, `422`, `500` |
| `DELETE` | `/fornecedores/{fornecedor_id}` | sim | exclui um fornecedor sem vínculos | `204` | `401`, `404`, `409`, `422`, `500` |
| `POST` | `/produtos` | sim | cadastra um produto com saldo zero | `201` | `401`, `404`, `409`, `422`, `500` |
| `GET` | `/produtos` | não | lista e filtra produtos | `200` | `422`, `500` |
| `GET` | `/produtos/estoque-baixo` | não | lista produtos no mínimo ou abaixo dele | `200` | `422`, `500` |
| `GET` | `/produtos/{produto_id}` | não | busca um produto | `200` | `404`, `422`, `500` |
| `PATCH` | `/produtos/{produto_id}` | sim | altera os dados do catálogo | `200` | `401`, `404`, `409`, `422`, `500` |
| `DELETE` | `/produtos/{produto_id}` | sim | exclui um produto sem movimentações | `204` | `401`, `404`, `409`, `422`, `500` |
| `POST` | `/movimentacoes` | sim | registra entrada ou saída | `201` | `401`, `404`, `409`, `422`, `500` |
| `GET` | `/movimentacoes` | não | lista e filtra o histórico | `200` | `400`, `422`, `500` |
| `GET` | `/movimentacoes/{movimentacao_id}` | não | busca uma movimentação | `200` | `404`, `422`, `500` |
| `GET` | `/health` | não | verifica se a API está disponível | `200` | `500` |

As listagens recebem `offset`, iniciado em zero, e `limite`, entre 1 e 100.

### Exemplos de requisição

Criar uma categoria:

```json
{
  "nome": "Papelaria"
}
```

Criar um fornecedor:

```json
{
  "nome": "Atacado Central",
  "cnpj": "12.345.678/0001-90",
  "telefone": "75999999999",
  "email": "contato@atacadocentral.com.br"
}
```

O CNPJ pode ser enviado com máscara, mas é normalizado para conter somente os 14 números.

Criar um produto:

```json
{
  "nome": "Caderno universitário",
  "sku": "CAD-001",
  "preco_custo": "10.00",
  "preco_venda": "18.00",
  "estoque_minimo": 5,
  "categoria_id": 1,
  "fornecedor_id": 1
}
```

Atualizar parcialmente um produto:

```json
{
  "preco_venda": "19.90",
  "estoque_minimo": 8
}
```

Registrar uma entrada:

```json
{
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 20,
  "observacao": "Compra do fornecedor"
}
```

Para registrar uma saída, o corpo é o mesmo e `tipo` recebe `saida`.

Os schemas completos, campos obrigatórios, exemplos e respostas de cada endpoint estão no Swagger.

## Consultas avançadas

Produtos podem ser filtrados por `nome`, `categoria_id` e `fornecedor_id`:

```http
GET /api/v1/produtos?nome=caderno&categoria_id=1
```

O endpoint de estoque baixo compara o saldo atual com o estoque mínimo diretamente no banco:

```http
GET /api/v1/produtos/estoque-baixo
```

O histórico aceita `data_inicio`, `data_fim`, `fornecedor_id`, `produto_id` e `tipo`:

```http
GET /api/v1/movimentacoes?data_inicio=2026-10-01&data_fim=2026-10-10&fornecedor_id=1&tipo=entrada
```

## Regras de estoque

- Todo produto começa com saldo zero.
- O saldo não pode ser alterado diretamente pela rota de produtos.
- Uma entrada soma a quantidade ao saldo.
- Uma saída subtrai a quantidade do saldo.
- Uma saída maior que o saldo disponível é recusada por inteiro.
- Saldo e movimentação são gravados na mesma transação.
- Movimentações não podem ser editadas nem excluídas pela API.
- Produtos com movimentações não podem ser excluídos.
- Categorias e fornecedores em uso também não podem ser excluídos.

Durante uma movimentação, o produto é consultado com `SELECT ... FOR UPDATE`. Esse bloqueio mantém
o registro protegido até o fim da transação e evita que duas saídas simultâneas leiam o mesmo saldo
antes de atualizá-lo.

## Respostas e erros

Os status de sucesso usados pela API são:

- `200 OK` para consultas e atualizações;
- `201 Created` para cadastros e movimentações;
- `204 No Content` para exclusões.

Erros seguem o mesmo formato em todas as rotas:

```json
{
  "erro": {
    "codigo": "ESTOQUE_INSUFICIENTE",
    "mensagem": "O produto não possui estoque suficiente para essa saída."
  }
}
```

| Status | Quando é utilizado |
| --- | --- |
| `400` | regra inválida, como período inicial maior que o final |
| `401` | autenticação ausente, inválida ou expirada |
| `404` | recurso não encontrado |
| `409` | duplicidade, vínculo existente ou estoque insuficiente |
| `422` | body, path ou query fora do formato esperado |
| `500` | erro interno não previsto |

Erros de validação também incluem o campo que causou o problema. Erros inesperados são registrados
no log, mas detalhes técnicos e stack traces não são enviados ao cliente.

## Testes e qualidade

Com um ambiente Python 3.12 ativo, instale as dependências de desenvolvimento:

```bash
python -m venv .venv
```

Ativação no Linux ou macOS:

```bash
source .venv/bin/activate
```

Ativação no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois, instale e execute as verificações:

```bash
pip install -e ".[dev]"
pytest -q
ruff format --check .
ruff check .
```

Os testes cobrem autenticação, documentação OpenAPI, categorias, fornecedores, produtos,
movimentações, validações, erros e atualização de estoque. Há também um teste específico com
PostgreSQL que dispara duas saídas simultâneas para validar o bloqueio do produto.

O workflow em `.github/workflows/testes.yml` executa as verificações em cada push e pull request da
branch `main`. Ele inicia um PostgreSQL limpo, aplica todas as migrations e só então roda os testes.

## Decisões técnicas

- **Services para regras de negócio:** evita misturar regras de estoque com detalhes das rotas.
- **Migrations com Alembic:** permite evoluir o banco sem recriar as tabelas manualmente.
- **`Decimal` para valores monetários:** evita os erros de precisão comuns do tipo `float`.
- **Restrições no banco e na aplicação:** validações amigáveis são feitas no service, enquanto
  índices únicos, chaves estrangeiras e checks mantêm uma última barreira de integridade.
- **Movimentações imutáveis:** preservam o histórico usado para auditoria.
- **JWT com expiração:** protege as operações de escrita sem impedir consultas públicas.
- **Lock pessimista:** prioriza a consistência do saldo quando existem alterações concorrentes.
- **Nomes do domínio em português:** deixam as entidades e regras próximas do problema apresentado.

## Uso de IA

Usei IA como apoio para discutir a estrutura inicial, revisar validações, investigar erros e montar
parte dos testes. As sugestões não foram mantidas automaticamente: revisei nomes, mensagens,
relacionamentos e regras para que combinassem com o desafio e com o que consigo explicar.

Entre os pontos reescritos ou ajustados durante o desenvolvimento estão a atualização transacional
do estoque, a preservação do fornecedor no histórico, o tratamento centralizado de erros e os
comentários do código. O arquivo [docs/DEFESA.md](docs/DEFESA.md) reúne os principais pontos que
preciso dominar para a apresentação técnica.

## Autor

Desenvolvido por Matheus Rodrigues para o processo seletivo da Ecomp Jr. - 2026.2.
