# Migração do aula-projeto-legado para o aula-projeto-novo

## Informações da atividade

- Categoria de Grupo: Grupos
- Nome do Grupo: Grupo 2
- Projeto Legado: https://github.com/guiigos/aula-projeto-legado

## Contexto

O backend atual do Sistema de Estacionamento foi desenvolvido em Java 8 puro, utilizando HttpServer nativo, JDBC e roteamento manual. Esta atividade propõe a migração completa desse backend para Python com Django, mantendo o mesmo banco de dados PostgreSQL, os mesmos endpoints REST e as mesmas regras de negócio.

## Objetivo

Reescrever o backend em Python + Django, substituindo:

| Java 8 | Python + Django |
|---|---|
| `com.sun.net.httpserver.HttpServer` | Django (views + urls) |
| JDBC + PreparedStatement | Django ORM |
| Gson | JsonResponse / json nativo |
| Roteamento manual | `urls.py` |
| Transações JDBC manuais | Verificações com ORM + if / raise |
| BigDecimal | DecimalField / Decimal |
| java.time.LocalDateTime | DateTimeField / datetime |
| PostgreSQL + init.sql | SQLite + `python manage.py migrate` |

O frontend (HTML + CSS + JS) não deve ser alterado. O banco de dados será trocado de PostgreSQL para SQLite, gerenciado inteiramente pelo Django via migrations.

## Tecnologias permitidas

- Python 3.11+
- Django 4.2+ (incluindo Django ORM, migrations e Views)
- SQLite (já embutido no Python, nenhum driver externo necessário)
- Somente bibliotecas da stdlib do Python além do Django

### Não utilizar

- Django REST Framework
- FastAPI, Flask ou qualquer outro framework web
- Serializers externos (ex.: Marshmallow, Pydantic)
- Celery, Redis ou filas de mensagens
- Autenticação ou sessões Django

## Estrutura esperada do projeto

```text
backend-django/
├── manage.py
├── requirements.txt
├── db.sqlite3               ← criado automaticamente após migrate
├── estacionamento/          ← projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api/                     ← app Django
    ├── models.py
    ├── urls.py
    ├── migrations/          ← gerado pelo Django
    │   └── 0001_initial.py
    ├── views/
    │   ├── __init__.py
    │   ├── cliente_views.py
    │   ├── veiculo_views.py
    │   ├── vaga_views.py
    │   ├── permanencia_views.py
    │   └── dashboard_views.py
    └── services/
        └── permanencia_service.py
```

## Tarefas

### Tarefa 1 — Configuração do projeto

Criar o projeto Django com `django-admin startproject estacionamento` e o app `api` com `python manage.py startapp api`.

Configurar `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Também:

- adicionar o app `api` em `INSTALLED_APPS`;
- configurar `ALLOWED_HOSTS = ['*']`;
- configurar `USE_TZ = False`;
- desativar CSRF para a API usando o middleware customizado da Tarefa 6;
- criar `requirements.txt` apenas com Django;
- executar `python manage.py makemigrations api`;
- executar `python manage.py migrate`.

### Tarefa 2 — Models e migrations

Criar os models em `api/models.py`. O Django gerenciará as tabelas via migrations; não usar `managed = False`.

Modelo de referência:

```python
class Cliente(models.Model):
    nome     = models.CharField(max_length=100)
    cpf      = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email    = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'clientes'
```

Implementar:

- `Cliente` → tabela `clientes`;
- `Veiculo` → tabela `veiculos`, FK para `Cliente`;
- `Vaga` → tabela `vagas`, choices `CARRO`/`MOTO`, `LIVRE`/`OCUPADA`, default `LIVRE`;
- `Permanencia` → tabela `permanencias`, FK para `Veiculo` e `Vaga`, `DecimalField` para valor, `DateTimeField` para datas e default `ABERTO`.

Após definir ou alterar os models, executar:

```bash
python manage.py makemigrations api
python manage.py migrate
```

### Tarefa 3 — Views e roteamento

Implementar cada endpoint como function-based view do Django retornando `JsonResponse`. Cada view deve verificar `request.method`, ler JSON com `json.loads(request.body)`, retornar o código HTTP correto, tratar erros com `JsonResponse({'error': '...'}, status=4xx)` e adicionar cabeçalhos CORS.

| Método | URL | View |
|---|---|---|
| GET / POST | `/api/clientes/` | `cliente_views.lista_clientes` |
| GET / PUT / DELETE | `/api/clientes/<id>/` | `cliente_views.detalhe_cliente` |
| GET / POST | `/api/veiculos/` | `veiculo_views.lista_veiculos` |
| GET / PUT / DELETE | `/api/veiculos/<id>/` | `veiculo_views.detalhe_veiculo` |
| GET / POST | `/api/vagas/` | `vaga_views.lista_vagas` |
| GET / PUT / DELETE | `/api/vagas/<id>/` | `vaga_views.detalhe_vaga` |
| POST | `/api/permanencias/entrada/` | `permanencia_views.entrada` |
| PUT | `/api/permanencias/<id>/saida/` | `permanencia_views.saida` |
| GET | `/api/permanencias/` | `permanencia_views.lista_permanencias` |
| GET | `/api/dashboard/` | `dashboard_views.dashboard` |

### Tarefa 4 — Serialização manual

Não utilizar serializers externos. Criar funções `to_dict()` para cada model:

- `cliente_to_dict`: `id`, `nome`, `cpf`, `telefone`, `email`;
- `veiculo_to_dict`: incluir `clienteNome` via `select_related`;
- `vaga_to_dict`;
- `permanencia_to_dict`: incluir `veiculoPlaca`, `veiculoModelo` e `vagaNumero`.

### Tarefa 5 — Serviço de permanência

Implementar `api/services/permanencia_service.py` usando apenas ORM básico (`filter`, `get`, `save`, `create`) e Python puro (`if`, `raise`, `datetime`, `Decimal`, `math.ceil`).

`registrar_entrada(veiculo_id, vaga_id)` deve:

1. Verificar com `.filter(...).exists()` se o veículo já tem permanência aberta e lançar `ValueError`;
2. buscar a vaga com `.get(id=vaga_id)`, tratando inexistência, e verificar se está `LIVRE`;
3. atualizar a vaga para `OCUPADA`;
4. criar a permanência com `datetime.now()` e status `ABERTO`.

`registrar_saida(permanencia_id)` deve:

1. buscar a permanência, verificando existência e status `ABERTO`;
2. calcular o valor com `_calcular_valor(entrada, saida)`;
3. preencher saída, valor e status `FINALIZADO`;
4. liberar a vaga.

Regras de `_calcular_valor`:

- tarifa de R$ 5,00 por hora;
- mínimo de 1 hora;
- frações de hora arredondadas para cima com `math.ceil`;
- cálculo monetário usando `Decimal`, sem `float`.

### Tarefa 6 — CORS

Criar `estacionamento/middleware.py` com middleware simples, sem pacotes externos. Para requisições `OPTIONS`, retornar resposta 204. Em todas as respostas, adicionar os cabeçalhos CORS, incluindo `Access-Control-Allow-Origin: *`. Registrar o middleware no `MIDDLEWARE` do `settings.py` antes dos demais.

### Tarefa 7 — Docker

Com SQLite, remover o serviço PostgreSQL, seu volume e as dependências correspondentes do `docker-compose.yml`:

```yaml
services:
  backend:
    build: ./backend-django
    ports:
      - "8080:8080"
    volumes:
      - sqlite_data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  sqlite_data:
```

Criar `backend-django/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DB_PATH=/app/data/db.sqlite3
RUN mkdir -p /app/data
EXPOSE 8080
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8080"]
```

O `settings.py` deve ler `DB_PATH` com `os.environ.get('DB_PATH', BASE_DIR / 'db.sqlite3')`.

### Tarefa 8 — Validação

Implementar validações equivalentes às do backend Java:

- nome e CPF obrigatórios em Cliente;
- placa, marca, modelo, cor e `clienteId` obrigatórios em Veículo;
- número e tipo obrigatórios em Vaga; tipo deve ser `CARRO` ou `MOTO`;
- `veiculoId` e `vagaId` obrigatórios na entrada;
- HTTP 409 para CPF, placa ou número de vaga duplicados;
- HTTP 409 se o veículo já estiver estacionado;
- HTTP 409 se a vaga estiver ocupada;
- HTTP 404 para recursos inexistentes.

## Critérios de aceite

- backend Django respondendo em `http://localhost:8080`;
- todos os endpoints funcionando;
- frontend existente sem alterações e funcionando normalmente;
- entrada e saída aplicando corretamente as regras de negócio;
- cálculo correto do valor de permanência;
- `docker compose up --build -d` funcionando sem PostgreSQL;
- banco SQLite criado automaticamente via `migrate`;
- dados persistindo após `docker compose restart`;
- nenhuma biblioteca além do Django, sem `psycopg2` ou similar.

## Dicas

- usar `select_related('cliente')` em veículos;
- usar `select_related('veiculo', 'vaga')` em permanências;
- usar `.filter(...).exists()` para verificações;
- usar `.get(...)` quando o objeto deve existir e capturar `DoesNotExist`;
- lançar `ValueError` no serviço e retornar HTTP 409 nas views;
- usar `USE_TZ = False`;
- definir `valor_total` como `DecimalField(max_digits=10, decimal_places=2, null=True)`;
- nunca versionar `db.sqlite3`; adicionar ao `.gitignore`;
- executar `migrate` no CMD do Docker.

## Frontend apontando para o backend local

O frontend usa URLs relativas (`/api/clientes`, `/api/vagas`, etc.), que funcionam quando servido pelo Nginx com proxy para o backend. Ao executar localmente sem Docker, há duas opções.

### Opção A — variável de base no `api.js`

Adicionar no topo de `frontend/js/api.js`:

```javascript
const API_BASE = 'http://localhost:8080';
```

Prefixar `get`, `post`, `put` e `delete` com `API_BASE + url`. Em produção, deixar `API_BASE` como string vazia. O backend deve retornar `Access-Control-Allow-Origin: *`.

### Opção B — Nginx local

No `frontend/nginx.conf`, trocar `backend:8080` por `127.0.0.1:8080` e executar o Nginx localmente. No Windows, fazer a alteração manualmente e executar:

```bash
cd frontend
nginx -p . -c nginx.conf
```

## Resumo dos endereços em desenvolvimento local

| Serviço | Endereço |
|---|---|
| Backend Django | `http://localhost:8080` |
| Frontend (Nginx local) | `http://localhost:3000` |
| Frontend aberto diretamente | `file://...` — não funciona com URLs relativas |

## Estado atual

Por enquanto, não iniciar a migração. Esta etapa cria somente a estrutura de documentação e memória para uso futuro da IA.
