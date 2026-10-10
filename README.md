# Ecomp Stock API

API de gerenciamento de produtos, fornecedores, categorias e movimentacoes de estoque.

## Estado atual

O projeto ja possui:

- configuracao do PostgreSQL e migrations com Alembic;
- modelos de categoria, fornecedor, produto e movimentacao de estoque;
- CRUD de categorias e fornecedores;
- resposta padronizada para erros de negocio;
- testes iniciais da API.

## Execucao local

1. Copie `.env.example` para `.env`.
2. Execute `docker compose up --build`.
3. Acesse `http://localhost:8000/docs`.

O endpoint de saude fica disponivel em `GET /health`.

## Rotas disponiveis

As rotas atuais usam o prefixo `/api/v1`:

- `/categorias` para cadastrar, listar, consultar, atualizar e excluir categorias;
- `/fornecedores` para cadastrar, listar, consultar, atualizar e excluir fornecedores.
- `/produtos` para cadastrar, listar, filtrar, consultar, atualizar e excluir produtos;
- `/produtos/estoque-baixo` para consultar produtos no estoque minimo ou abaixo dele.

Produtos sao criados com estoque zero. A quantidade nao pode ser alterada pelo CRUD porque as
entradas e saidas serao registradas pelas rotas de movimentacao de estoque.

A documentacao interativa do FastAPI mostra os corpos e respostas esperados de cada rota.

