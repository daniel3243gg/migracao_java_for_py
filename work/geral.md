# Organização do trabalho — Migração para Django

## Objetivo

Migrar o backend Java do `aula-projeto-legado` para Python 3.11+ com Django 4.2+, mantendo os endpoints REST, as regras de negócio e o frontend existente sem alterações.

O roteiro completo está em [`../docs/roteiro-migracao.md`](../docs/roteiro-migracao.md).

## Ordem de execução

As tarefas devem ser executadas na ordem abaixo, pois cada etapa prepara a base para a próxima:

1. **Daniel** — análise do legado, planejamento técnico e criação da base Django;
2. **Breno** — views, serialização manual e roteamento dos cadastros;
3. **Theo** — models, migrations e configuração do banco SQLite;
4. **Gabs** — validação inicial, contratos da API e preparação dos testes;
5. **Petry** — CORS, Docker, integração com o frontend e configuração de execução;
6. **Lemos** — serviço de permanência, entrada, saída e regras de cálculo.

## Regras de colaboração

- Cada pessoa deve ler este arquivo e o seu arquivo individual antes de começar.
- A pessoa seguinte deve conferir a entrega da pessoa anterior antes de alterar a própria parte.
- Manter o frontend sem alterações funcionais, salvo a configuração de URL local explicitamente prevista no roteiro.
- Não adicionar bibliotecas fora do Django e da biblioteca padrão do Python.
- Não versionar `db.sqlite3`.
- Registrar pendências, decisões e problemas no arquivo individual correspondente.
- Ao concluir uma etapa, atualizar o status no arquivo individual e deixar instruções claras para a próxima pessoa.
- Evitar reescrever ou desfazer o trabalho de outra pessoa sem registrar o motivo.

## Dependências entre etapas

```text
Daniel → Breno → Theo → Gabs → Petry → Lemos
```

## Definition of Done geral

- Backend Django executando em `http://localhost:8080`.
- SQLite criado e atualizado por migrations.
- Endpoints definidos no roteiro funcionando com os códigos HTTP esperados.
- Regras de permanência e cálculo financeiro corretas.
- CORS configurado sem dependência externa.
- Docker Compose funcionando sem PostgreSQL.
- Dados persistindo no volume SQLite.
- Frontend existente funcionando sem alteração de comportamento.
- Validações e critérios de aceite verificados.

## Status geral

- [ ] Daniel — análise e fundação
- [ ] Breno — views e roteamento
- [ ] Theo — models e migrations
- [ ] Gabs — validação inicial e testes
- [ ] Petry — infraestrutura e integração
- [ ] Lemos — permanência e validação final
