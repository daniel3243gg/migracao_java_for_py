# Aula Projeto Novo

Migração do backend do sistema de estacionamento para Python + Django, conforme
a documentação em `docs/roteiro-migracao.md`.

## Estado

O backend está em `backend-django/` com todas as tarefas do roteiro: configuração,
models e migrations, views e serialização, serviço de permanência (entrada, saída e
cálculo da tarifa), CORS, Docker e validações. O frontend em `frontend/` é uma cópia
sem alterações do `aula-projeto-legado`.

- Python 3.11 ou superior (o Docker usa 3.11; 3.14 local também funciona).
- Django 5.2 LTS (`Django>=5.2,<6.0`), única dependência.
- SQLite criado por `migrate`. A migration `0002_seed_vagas` cadastra as 15
  vagas iniciais do legado (A01 a A10 carro, B01 a B05 moto).

## Desenvolvimento local

```bash
cd backend-django
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8080
```

O banco local será criado como `backend-django/db.sqlite3` (fora do git). Para
usar outro arquivo, defina `DB_PATH`.

## Testes

```bash
cd backend-django
. .venv/bin/activate
python manage.py test api
python manage.py makemigrations --check --dry-run   # deve dizer "No changes detected"
```

## Aviso: banco criado antes da Tarefa 2 revisada

A `0001_initial.py` foi regenerada pelo Django. Quem já tinha rodado `migrate`
com a versão anterior precisa apagar o banco local e migrar de novo:

```bash
cd backend-django
rm -f db.sqlite3
python manage.py migrate
```

## Docker (Tarefa 7)

O `docker-compose.yml` sobe só o backend Django e o frontend Nginx; não há mais
PostgreSQL. O SQLite fica no volume `sqlite_data` (`/app/data/db.sqlite3`) e o
`migrate` roda sempre que o container inicia.

```bash
docker compose up --build -d     # frontend em http://localhost:3000, API em http://localhost:8080
docker compose restart           # os dados continuam lá
docker compose down -v           # apaga também o volume do banco
```

## Permanências e validações (Tarefas 5 e 8)

| Situação | HTTP | Mensagem |
| --- | --- | --- |
| `veiculoId` ou `vagaId` ausente/inválido | 400 | `Campos 'veiculoId' e 'vagaId' são obrigatórios` |
| Veículo já estacionado | 409 | `Veículo já possui uma permanência em aberto.` |
| Vaga ocupada | 409 | `Vaga já está ocupada.` |
| Vaga ou veículo inexistente | 404 | `Vaga não encontrada.` / `Veículo não encontrado.` |
| Saída de permanência inexistente | 404 | `Permanência não encontrada.` |
| Saída de permanência já finalizada | 409 | `Permanência já foi finalizada.` |

Tarifa: R$ 5,00 por hora, mínimo de 1 hora, frações arredondadas para cima com
`math.ceil`, tudo em `Decimal`. Os cadastros já validavam campos obrigatórios,
`tipo` de vaga e duplicidade de CPF, placa e número de vaga (409).
