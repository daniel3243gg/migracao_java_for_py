# 03 — Breno

## Responsabilidade

Implementar as views CRUD, a serialização manual e o roteamento dos cadastros.

## Pré-requisito

Daniel deve ter concluído a análise e deixado a estrutura `backend-django/` inicializada.

## Tarefas

- [ ] Criar a estrutura `api/views/` e `api/urls.py`.
- [ ] Implementar `cliente_views.py` para listar, criar, consultar, atualizar e excluir clientes.
- [ ] Implementar `veiculo_views.py` para listar, criar, consultar, atualizar e excluir veículos.
- [ ] Implementar `vaga_views.py` para listar, criar, consultar, atualizar e excluir vagas.
- [ ] Implementar `to_dict()` manual para cada model.
- [ ] Usar `select_related('cliente')` nos veículos.
- [ ] Validar JSON, métodos HTTP, campos obrigatórios e duplicidades.
- [ ] Retornar HTTP 404, 409 e 400 conforme o roteiro.
- [ ] Configurar o include das URLs da API no projeto Django.
- [ ] Testar os endpoints CRUD com requisições locais.

## Entrega para Theo

API de cadastros e contratos JSON documentados, para que Theo possa conferir a compatibilidade dos models com as views.

## Status

- [ ] Não iniciado
