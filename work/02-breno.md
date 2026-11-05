# 03 — Breno

## Responsabilidade

Implementar as views CRUD, a serialização manual e o roteamento dos cadastros.

## Pré-requisito

Daniel deve ter concluído a análise e deixado a estrutura `backend-django/` inicializada.

## Tarefas

- [x] Criar a estrutura `api/views/` e `api/urls.py`.
- [x] Implementar `cliente_views.py` para listar, criar, consultar, atualizar e excluir clientes.
- [x] Implementar `veiculo_views.py` para listar, criar, consultar, atualizar e excluir veículos.
- [x] Implementar `vaga_views.py` para listar, criar, consultar, atualizar e excluir vagas.
- [x] Implementar `to_dict()` manual para cada model.
- [x] Usar `select_related('cliente')` nos veículos.
- [x] Validar JSON, métodos HTTP, campos obrigatórios e duplicidades.
- [x] Retornar HTTP 404, 409 e 400 conforme o roteiro.
- [x] Configurar o include das URLs da API no projeto Django.
- [x] Testar os endpoints CRUD com requisições locais.

## Entrega para Theo

API de cadastros e contratos JSON documentados, para que Theo possa conferir a compatibilidade dos models com as views.

## Status

- [x] Views CRUD de clientes, veículos e vagas, dashboard, `to_dict` e rotas: concluído (change OpenSpec `views-cadastros-e-dashboard`)
- [x] Revisão das Tarefas 1 e 2 (fundação e models): concluída no branch `breno/fundacao-django-e-models`

## Registro: revisão das Tarefas 1 e 2

Antes de começar as views, conferi a fundação (Daniel) e os models (Theo) contra o `database/init.sql` e os controllers do legado. Encontrei problemas que afetariam todas as etapas seguintes, então corrigi e registro aqui o motivo, como pede `work/geral.md`.

O que mudou em `aula-projeto-novo/backend-django/` (só correções; o resto ficou como estava):

- `requirements.txt`: `Django>=5.2,<6.0`. Com Django 4.2 no Python 3.14, o test client do Django quebra (`AttributeError: 'super' object has no attribute 'dicts'` em `Context.__copy__`) sempre que uma resposta de erro é registrada. O servidor roda, mas os testes da API não. A 4.2 também saiu de suporte em abril de 2026. A 5.2 LTS roda no 3.11 do Docker e no 3.14 e continua dentro de "Django 4.2+".
- `settings.py`: saíram `auth`, `sessions`, `messages`, os middlewares e context processors correspondentes. O roteiro proíbe autenticação e sessões do Django.
- `api/models.py`:
  - `CheckConstraint` para `vagas.tipo`, `vagas.status` e `permanencias.status` (o `choices` sozinho não cria nada no banco; o legado tinha `CHECK`);
  - `data_hora_entrada` com `default=datetime.now` em vez de `auto_now_add`, que ignorava o horário passado pelo serviço (Tarefa 5) e impedia testar o cálculo.
- `api/migrations/0001_initial.py` regenerada pelo Django. A versão escrita à mão divergia dos models: `makemigrations --check` gerava uma migration de renomeação de índices.
- `api/migrations/0002_seed_vagas.py` (nova): as 15 vagas do `init.sql` (A01 a A10 carro, B01 a B05 moto), sem duplicar nem sobrescrever. Sem ela, um banco novo começava sem nenhuma vaga.
- `api/tests/`: 30 testes de schema e configuração (`python manage.py test api`).

Os models não têm `Meta.ordering`: a ordenação do legado (cliente por nome, veículo por placa, vaga por número, permanência pela entrada mais recente) deve ser feita com `order_by` nas views.

**Atenção:** quem já rodou `migrate` com a `0001` antiga precisa apagar o `db.sqlite3` local e migrar de novo.

Para as próximas etapas (views, serviço, CORS, Docker), o inventário completo das regras do legado, com mensagens de erro exatas, códigos HTTP, ordem das validações e a tabela do cálculo, está em `openspec/changes/fundacao-django-e-models/design.md`. Pontos que mais pegam:

- o frontend chama `/api/...` sem barra final; as rotas precisam aceitar com e sem barra;
- o cálculo descarta os segundos antes de arredondar (60 min 59 s custa R$ 5,00);
- o legado responde 404 para vaga ou permanência inexistente e 409 para conflito; o roteiro manda tratar `ValueError` como 409, então inexistência precisa de uma subclasse própria tratada como 404.

## Registro: views de cadastro e dashboard (Tarefa 3)

Implementado em `aula-projeto-novo/backend-django/`:

- `api/views/cliente_views.py`, `veiculo_views.py`, `vaga_views.py`: CRUD com as mensagens e códigos HTTP do backend Java, na mesma ordem de validação.
- `api/views/dashboard_views.py`: `GET /api/dashboard` (não tinha dono em `work/`, entrou junto).
- `api/views/comum.py`: respostas JSON, leitura do corpo, conversão de ID e o tratamento de erro de banco (500).
- `api/serializacao.py`: `cliente_to_dict`, `veiculo_to_dict`, `vaga_to_dict` e `permanencia_to_dict`.
- `api/urls.py`: toda rota responde com e sem barra final.
- Testes em `api/tests/test_api_*.py` e `test_serializacao.py`.

Divergências deliberadas do Java (Tarefa 8 do roteiro ou casos em que o Java não respondia):

- CPF, placa ou número de vaga repetido na **edição**: 409 (Java: 500);
- veículo com `clienteId` inexistente: 404 `Cliente não encontrado` (Java: 500);
- `POST` em `/api/<recurso>/<id>`: 405 (Java criava um registro novo ignorando o ID);
- corpo que não é objeto JSON: 400 `JSON inválido` (Java: sem resposta).

**Para Lemos (Tarefa 5):**

- `api/urls.py` agora aceita barra final também em `/api/permanencias`, `/api/permanencias/entrada` e `/api/permanencias/<id>/saida`. Nomes das views e assinaturas (`saida(request, permanencia_id)` com `int`) não mudaram.
- `permanencia_to_dict` já está em `api/serializacao.py` (use `select_related('veiculo', 'vaga')`). `valorTotal` sai como número JSON; o cálculo continua em `Decimal`.
- `api/views/comum.py` tem `responder`, `erro`, `ler_json`, `converter_inteiro` e o decorator `tratar_erro_banco`, prontos para reaproveitar.
