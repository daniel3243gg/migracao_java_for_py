# Memória da IA — Migração do projeto

## Objetivo

Migrar futuramente o backend de `aula-projeto-legado` para um novo backend Django em Python, conforme o roteiro em [`docs/roteiro-migracao.md`](../docs/roteiro-migracao.md).

## Estado atual

- Migração em andamento. Backend Django em `aula-projeto-novo/backend-django/`.
- Tarefa 1 (configuração) concluída: Django 5.2 LTS, sem auth, sessões, mensagens nem CSRF, SQLite via `DB_PATH`, `USE_TZ = False`, `APPEND_SLASH = False`.
- Tarefa 2 (models e migrations) concluída: models com `CheckConstraint` do `init.sql` e `data_hora_entrada` atribuível, `0001_initial` gerada pelo Django, `0002_seed_vagas` com as 15 vagas iniciais, testes em `api/tests/`. Detalhes e motivo em `work/02-breno.md`.
- Tarefa 3 (parte de cadastros) concluída: views de clientes, veículos, vagas e dashboard, serialização manual em `api/serializacao.py` e rotas com e sem barra final. Detalhes em `work/02-breno.md`.
- Tarefa 5 (serviço e views de permanência) concluída: entrada, saída, listagem e cálculo em `Decimal` (R$ 5,00/h, mínimo 1 h, `math.ceil`). Regra violada levanta `ValueError` (409); recurso inexistente levanta `NaoEncontrado`, subclasse de `ValueError` (404).
- Tarefa 7 (Docker) concluída: `aula-projeto-novo/docker-compose.yml` só com backend e frontend, volume `sqlite_data` em `/app/data`, `migrate` no início do container.
- Tarefa 8 (validação) concluída: entrada exige `veiculoId` e `vagaId`; 409 para veículo estacionado, vaga ocupada e duplicidades; 404 para recurso inexistente. Testes em `api/tests/test_api_permanencias.py`.
- `aula-projeto-novo/frontend/` é cópia sem alterações do frontend do `aula-projeto-legado`.
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
