# 04 — Gabs

## Responsabilidade

Preparar a validação inicial, consolidar contratos da API e criar a base de testes para as próximas etapas.

## Pré-requisito — revisão da etapa de Theo

Não existe `work/04-theo.md` neste repositório. A etapa de Theo disponível é `work/03-theo.md`, identificada também no fluxo de `work/geral.md` e no registro de Breno.

Revisão estática de `aula-projeto-novo/backend-django/api/models.py` e `api/migrations/`:

- Os quatro modelos (`Cliente`, `Veiculo`, `Vaga`, `Permanencia`) e os nomes de tabela previstos estão presentes.
- FKs, `on_delete`, campos obrigatórios/opcionais, unicidade, choices, defaults, `DecimalField` e `DateTimeField` estão definidos.
- Há constraints de banco para os domínios de tipo/status; a migration inicial corresponde aos models.
- A segunda migration semeia as 15 vagas iniciais, sem sobrescrever números já existentes.
- Existem testes de schema, constraints, FKs, migrations e seed em `api/tests/test_models.py`.

**Resultado:** revisão estática e runtime concluídas. `makemigrations --check --dry-run` retornou `No changes detected`; `migrate --check` terminou com código 0; os testes de schema estão incluídos na suíte aprovada.

## Tarefas

- [x] Criar matriz de endpoints, métodos, payloads e respostas esperadas em `docs/matriz-testes-api.md`.
- [x] Consolidar contratos JSON de clientes, veículos, vagas e permanências para Petry e Lemos.
- [x] Conferir a cobertura existente de criação, edição, consulta, exclusão, duplicidades e recursos inexistentes nos testes de API.
- [x] Acrescentar cobertura para os métodos HTTP permitidos/recusados nas coleções e itens CRUD em `api/tests/test_api_metodos.py`.
- [x] Executar a suíte de testes CRUD e confirmar os resultados em runtime: 125 testes aprovados.
- [x] Verificar as tentativas de entrada nos cenários de veículo já estacionado e vaga ocupada; ambas retornam `501` antes de validar o estado, pois a view ainda é stub. Registrar o bloqueio para Lemos; os `409` esperados só podem ser verificados após a implementação.
- [x] Registrar os bugs e encaminhamentos abaixo.

## Bugs e pendências encaminhados

- **Lemos — implementação de permanência:** `api/views/permanencia_views.py` retorna `501` para listar, registrar entrada e registrar saída; `api/services/permanencia_service.py` lança `NotImplementedError`. As duas requisições de entrada simuladas (veículo já estacionado e vaga ocupada) responderam `501`, portanto não chegaram às validações de conflito. Permanecem sem verificação os `409` desses casos, `404` de permanência inexistente e liberação da vaga na saída. A matriz registra o contrato esperado.
- **Suíte e migrations:** `manage.py test api.tests` — 125 testes aprovados; `makemigrations --check --dry-run` — `No changes detected`; `migrate --check` — código 0.
- **Organização — nome do arquivo de Theo:** a solicitação menciona `04-theo.md`, que não existe; revisão feita contra `03-theo.md`.

## Entrega para Petry

Matriz e contratos em [`docs/matriz-testes-api.md`](../docs/matriz-testes-api.md), cobertura automatizada existente e novo teste de métodos HTTP. A suíte foi executada; a implementação de permanência continua como pendência encaminhada para Lemos.

## Status

- [x] Matriz e contratos preparados; cobertura CRUD revisada.
- [x] Validação runtime e matriz concluídas; pendência de implementação de permanência encaminhada para Lemos.
