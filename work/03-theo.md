# 02 — Theo

## Responsabilidade

Implementar os models Django e o banco SQLite gerenciado por migrations.

## Pré-requisito

Breno deve ter documentado os contratos da API e Daniel deve ter deixado a estrutura `backend-django/` inicializada.

## Tarefas

- [ ] Conferir o mapeamento do legado e o roteiro.
- [ ] Implementar `Cliente`, `Veiculo`, `Vaga` e `Permanencia` em `api/models.py`.
- [ ] Configurar nomes das tabelas com `db_table` conforme o roteiro.
- [ ] Configurar FKs, campos obrigatórios, campos opcionais, choices, defaults e unicidade.
- [ ] Configurar `DecimalField` e `DateTimeField` corretamente.
- [ ] Gerar `makemigrations` e aplicar `migrate`.
- [ ] Confirmar que as tabelas e restrições foram criadas no SQLite.
- [ ] Atualizar a documentação se algum campo exigir decisão.

## Entrega para Gabs

Models estáveis, migrations aplicadas e exemplos dos campos disponíveis para os testes.

## Status

- [ ] Não iniciado
