# Matriz de testes e contrato inicial da API

Esta matriz consolida os contratos observados nas views e no roteiro de migração. Os exemplos usam JSON UTF-8 e os caminhos sem barra final usados pelo frontend; a API também aceita a barra final.

## Endpoints e métodos

| Recurso | Método | Entrada | Resposta esperada | Cobertura/estado |
|---|---|---|---|---|
| `/api/clientes` | GET | — | `200`, lista ordenada por nome | Coberto em `test_api_clientes.py` |
| `/api/clientes` | POST | `{ "nome": "Ana", "cpf": "111.111.111-11", "telefone": "", "email": "" }` | `201`, cliente criado | Coberto; campos obrigatórios e CPF duplicado também |
| `/api/clientes` | PUT/DELETE | — | `400`, `ID obrigatório` | Coberto em `test_api_contrato.py` |
| `/api/clientes/{id}` | GET | — | `200` com cliente; `404` se inexistente | Coberto |
| `/api/clientes/{id}` | PUT | mesmos campos de criação | `200`; `400` validação; `404` inexistente; `409` CPF duplicado | Coberto |
| `/api/clientes/{id}` | DELETE | — | `200`; `404` inexistente; `409` se houver histórico protegido | Coberto |
| `/api/veiculos` | GET | — | `200`, lista ordenada por placa com `clienteNome` | Coberto |
| `/api/veiculos` | POST | `{ "placa": "ABC1234", "marca": "Fiat", "modelo": "Uno", "cor": "Branco", "clienteId": 1 }` | `201`; `400` validação; `404` cliente inexistente; `409` placa duplicada | Coberto |
| `/api/veiculos` | PUT/DELETE | — | `400`, `ID obrigatório` | Coberto em `test_api_contrato.py` |
| `/api/veiculos/{id}` | GET | — | `200` com `clienteId` e `clienteNome`; `404` inexistente | Coberto |
| `/api/veiculos/{id}` | PUT | mesmos campos de criação | `200`; `400` validação; `404` veículo/cliente inexistente; `409` placa duplicada | Coberto |
| `/api/veiculos/{id}` | DELETE | — | `200`; `404` inexistente; `409` se houver permanência | Coberto |
| `/api/vagas` | GET | opcional `?status=LIVRE` | `200`, lista ordenada por número | Coberto |
| `/api/vagas` | POST | `{ "numero": "C01", "tipo": "CARRO" }` | `201`, status inicial `LIVRE`; `400` validação; `409` número duplicado | Coberto |
| `/api/vagas` | PUT/DELETE | — | `400`, `ID obrigatório` | Coberto em `test_api_contrato.py` |
| `/api/vagas/{id}` | GET | — | `200`; `404` inexistente | Coberto |
| `/api/vagas/{id}` | PUT | `{ "numero": "C01", "tipo": "CARRO", "status": "LIVRE" }` | `200`; `400` validação; `404` inexistente; `409` número duplicado | Coberto |
| `/api/vagas/{id}` | DELETE | — | `200`; `404` inexistente; `409` se houver permanência | Coberto |
| `/api/permanencias` | GET | — | `200`, lista de permanências com `veiculoPlaca`, `veiculoModelo` e `vagaNumero` | **Pendente:** view retorna `501` |
| `/api/permanencias/entrada` | POST | `{ "veiculoId": 1, "vagaId": 1 }` | `201`; `400` campos ausentes/inválidos; `404` recurso inexistente; `409` veículo já estacionado ou vaga ocupada | **Pendente:** view retorna `501` e serviço lança `NotImplementedError` |
| `/api/permanencias/{id}/saida` | PUT | — | `200` com permanência finalizada; `404` inexistente; `409` se já finalizada | **Pendente:** view retorna `501` e serviço lança `NotImplementedError` |
| `/api/dashboard` | GET | — | `200` com totais de vagas e veículos estacionados | Coberto em `test_api_dashboard.py` |

Em rotas sem ID, `PATCH` e demais métodos não suportados retornam `405`. Em rotas de item, métodos diferentes de `GET`, `PUT` e `DELETE` retornam `405`. JSON inválido ou que não seja objeto retorna `400` com `{"error":"JSON inválido"}`.

## Formatos de resposta

```json
{
  "id": 1,
  "nome": "Ana",
  "cpf": "111.111.111-11",
  "telefone": "",
  "email": ""
}
```

```json
{
  "id": 1,
  "placa": "ABC1234",
  "marca": "Fiat",
  "modelo": "Uno",
  "cor": "Branco",
  "clienteId": 1,
  "clienteNome": "Ana"
}
```

```json
{"id": 1, "numero": "A01", "tipo": "CARRO", "status": "LIVRE"}
```

Erros usam `{ "error": "mensagem" }`; exclusões bem-sucedidas usam `{ "message": "... excluído com sucesso" }`. A serialização de permanência já foi preparada em `api/serializacao.py`, mas falta integrar a view/serviço.

## Cenários mínimos de validação

| Grupo | Cenários |
|---|---|
| CRUD | Criar, listar, consultar, editar e excluir cliente, veículo e vaga; confirmar persistência e payload serializado |
| Unicidade | CPF, placa e número de vaga repetidos na criação e edição retornam `409` sem alterar o registro original |
| Ausência | GET/PUT/DELETE de ID inexistente retornam `404` |
| Métodos | Método permitido por rota; método inválido retorna `405`; PUT/DELETE em coleção retornam `400 ID obrigatório` |
| Permanência | Entrada com veículo já estacionado ou vaga ocupada retorna `409`; saída finaliza e libera a vaga; consultar coleção inclui os campos relacionados |

## Pendências e encaminhamento

- **Lemos — permanência (bloqueador):** `api/views/permanencia_views.py` ainda devolve `501` nos três endpoints e `api/services/permanencia_service.py` ainda lança `NotImplementedError`. Assim, os cenários de veículo já estacionado, vaga ocupada, 404 de permanência e saída não podem ser executados contra o contrato esperado. A matriz registra esses comportamentos para virar teste executável após a implementação.
- **Validação executada:** `manage.py test api.tests` aprovou 125 testes; `makemigrations --check --dry-run` respondeu `No changes detected`; `migrate --check` terminou com código 0. O teste de métodos HTTP está em `api/tests/test_api_metodos.py`.
- **Teste exploratório de permanência:** foram enviadas duas requisições POST de entrada, uma para cada cenário de conflito (veículo já estacionado e vaga ocupada); ambas retornaram `501`. Isso confirma que a view não chega à validação de conflito, então os `409` esperados continuam bloqueados até Lemos implementar o serviço e as views.
- **Theo — models/migrations:** revisão estática encontrou os quatro modelos, nomes de tabela, FKs, unicidade, constraints, defaults, campos decimais/data e migrations. `makemigrations --check --dry-run` confirmou ausência de alterações pendentes; `migrate --check` confirmou que o SQLite está atualizado. Os testes de schema passaram na suíte.
- **Divergência de arquivo:** não existe `work/04-theo.md`; a etapa de Theo disponível é `work/03-theo.md` (identificada como Theo no fluxo e no registro de Breno).
