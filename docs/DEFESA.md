# Roteiro para a defesa

Este arquivo é um resumo para revisar antes da apresentação. A ideia não é decorar respostas, mas conseguir seguir o caminho de uma requisição e explicar por que cada decisão foi tomada.

## 1. Problema de negócio

A loja precisa saber quais produtos vende, quem fornece cada produto e em qual categoria ele está. Também precisa confiar no saldo do estoque e consultar o histórico de entradas e saídas. Sem esses relacionamentos, uma venda pode usar um saldo errado e uma alteração de cadastro pode apagar parte da história da loja.

## 2. Organização do código

- `routes` recebe a requisição, declara o status HTTP e chama o service;
- `schemas` valida a entrada e controla o formato da resposta;
- `services` contém as regras de negócio e as transações;
- `models` representa as tabelas e seus relacionamentos;
- `migrations` mantém o histórico da estrutura do banco;
- `tests` verifica as regras pelos endpoints.

Exemplo para mostrar: em uma entrada de estoque, a rota recebe o JSON, `MovimentacaoCriacao` valida os campos e `criar_movimentacao` bloqueia o produto, altera o saldo e cria o histórico na mesma transação.

## 3. Decisões de modelagem

- Produto referencia categoria e fornecedor por chave estrangeira.
- SKU, CNPJ, e-mail do fornecedor, nome da categoria e e-mail do usuário possuem restrições de unicidade no banco.
- O saldo não aparece nos schemas de criação ou atualização do produto. Assim, ele só muda por movimentação.
- A movimentação guarda o fornecedor daquele momento. Se o produto trocar de fornecedor depois, o histórico antigo continua correto.
- Produtos e fornecedores com movimentações não podem ser excluídos, pois isso quebraria a auditoria.

## 4. Regras de estoque

Uma entrada soma a quantidade e uma saída subtrai. Antes da saída, o service confere se há saldo. Quando não há, ele faz rollback e retorna `409 ESTOQUE_INSUFICIENTE`.

Saldo e histórico são gravados por um único `commit`. Se qualquer parte falhar, o rollback desfaz a operação inteira.

Movimentações são imutáveis: existem apenas POST e GET. Não há PATCH nem DELETE para elas.

## 5. Concorrência

O `SELECT ... FOR UPDATE` bloqueia a linha do produto durante a movimentação. Se duas saídas chegarem juntas, uma espera a outra terminar e depois lê o saldo atualizado. Isso impede que as duas aprovem a venda usando o mesmo saldo.

SQLite é usado nos testes rápidos, mas não reproduz esse bloqueio como o PostgreSQL. Por isso existe um teste separado no GitHub Actions usando PostgreSQL real e duas threads.

## 6. Autenticação

No cadastro, a senha passa pelo Argon2 e apenas o hash é salvo. No login, a senha informada é comparada com esse hash. Se estiver correta, a API cria um JWT com o ID do usuário e horário de expiração.

As consultas ficaram públicas para facilitar a leitura do catálogo. Rotas que criam, alteram ou excluem dados exigem o token. O cadastro público é uma escolha simples para o escopo do desafio; em produção, ele poderia depender de convite ou de um administrador.

## 7. Erros e validação

Os schemas barram campos ausentes, formatos incorretos, valores negativos e campos extras. As regras que dependem do banco ficam nos services. Todos os erros seguem o formato `erro.codigo` e `erro.mensagem`.

Casos principais:

- `400`: período de consulta invertido;
- `401`: token ou credenciais inválidas;
- `404`: recurso não encontrado;
- `409`: duplicidade, vínculo que impede exclusão ou estoque insuficiente;
- `422`: corpo, parâmetro ou formato inválido;
- `500`: erro inesperado sem stack trace na resposta.

## 8. Testes e CI

Os testes cobrem os CRUDs, filtros, validações, atualização do saldo, imutabilidade, autenticação e concorrência. A cada push, o GitHub Actions confere a formatação, analisa o código, sobe PostgreSQL, aplica as migrations e roda a suíte.

## 9. Uso de IA

A IA foi usada para ajudar na estrutura inicial, revisar validações e sugerir testes. As partes que precisaram de mais revisão foram o controle de concorrência, a preservação do fornecedor no histórico e a padronização dos erros. Os nomes do domínio e a separação entre rotas, schemas, services e models foram mantidos porque deixam o fluxo mais fácil de explicar.

## 10. Perguntas que podem aparecer

**Por que `Decimal` nos preços?** Porque `float` pode introduzir erro de arredondamento em valores monetários.

**Por que Alembic?** Para evoluir o banco sem apagar os dados e para aplicar a mesma estrutura em desenvolvimento, teste e produção.

**Por que não alterar o estoque pelo PATCH do produto?** Porque isso criaria mudanças sem histórico e impediria a auditoria.

**Por que retornar 409 em estoque insuficiente?** A requisição é válida, mas entra em conflito com o estado atual do estoque.

**O que você melhoraria com mais tempo?** Perfis de acesso, refresh token, revogação de tokens, logs estruturados, paginação com total e implantação em um ambiente público.
