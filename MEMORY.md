# Memória da IA — Migração do projeto

## Objetivo

Migrar futuramente o backend de `aula-projeto-legado` para um novo backend Django em Python, conforme o roteiro em [`docs/roteiro-migracao.md`](../docs/roteiro-migracao.md).

## Estado atual

- Migração em andamento. Backend Django em `aula-projeto-novo/backend-django/`.
- Tarefa 1 (configuração) concluída: Django 5.2 LTS, sem auth, sessões, mensagens nem CSRF, SQLite via `DB_PATH`, `USE_TZ = False`, `APPEND_SLASH = False`.
- Tarefa 2 (models e migrations) concluída: models com `CheckConstraint` do `init.sql` e `data_hora_entrada` atribuível, `0001_initial` gerada pelo Django, `0002_seed_vagas` com as 15 vagas iniciais, testes em `api/tests/`. Detalhes e motivo em `work/02-breno.md`.
- Views, serviço de permanência, CORS completo e Docker Compose ainda pendentes (Tarefas 3 a 8).
- Nenhuma alteração feita no frontend ou no backend legado.
- A execução foi organizada para seis pessoas em `work/geral.md` e nos arquivos individuais de cada integrante.
- A ordem definida é: Daniel, Breno, Theo, Gabs, Petry e Lemos.

## Regras importantes

- Consultar sempre [`docs/regras-negocio/`](../docs/regras-negocio/) antes de analisar, responder ou implementar qualquer mudança relacionada às regras de negócio, entidades, fluxos ou contratos do sistema. Usar essa documentação como referência inicial e conferir o código quando houver divergência.
- Preservar o frontend existente sem alterações durante a migração.
- Usar Python 3.11+, Django 4.2+ e SQLite gerenciado por migrations.
- Usar somente Django e bibliotecas da stdlib; não usar Django REST Framework nem outros frameworks ou serializers externos.
- Manter os endpoints REST e as regras de negócio definidos no roteiro.
- Não versionar `db.sqlite3`.

## Próxima etapa

Antes de implementar, revisar a estrutura e o comportamento do projeto legado, especialmente modelos, endpoints, respostas JSON, validações e regras de permanência. Depois criar a estrutura `backend-django/` conforme o roteiro.

## Organização da equipe

O plano detalhado de execução está em [`../work/geral.md`](../work/geral.md). A migração ainda não foi iniciada.
