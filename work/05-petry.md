# 05 — Petry

## Responsabilidade

Configurar CORS, Docker e integração de execução com o frontend existente.

## Pré-requisito

Gabs deve ter consolidado os contratos e Theo deve ter concluído os models e migrations.

## Tarefas

- [ ] Implementar `estacionamento/middleware.py` com CORS manual.
- [ ] Tratar requisições `OPTIONS` com HTTP 204.
- [ ] Adicionar cabeçalhos CORS em todas as respostas.
- [ ] Configurar o middleware no `settings.py`.
- [ ] Criar ou ajustar `backend-django/Dockerfile`.
- [ ] Atualizar `docker-compose.yml` para remover PostgreSQL.
- [ ] Configurar o volume persistente do SQLite em `/app/data`.
- [ ] Configurar `DB_PATH` e execução automática de `migrate` no container.
- [ ] Verificar a comunicação entre frontend e backend.
- [ ] Ajustar somente a base da API local se isso for necessário e previsto no roteiro.
- [ ] Testar `docker compose up --build -d` e reinicialização dos serviços.

## Entrega para Lemos

Ambiente executando com Docker, CORS funcional e frontend comunicando com o backend.

## Status

- [ ] Não iniciado
