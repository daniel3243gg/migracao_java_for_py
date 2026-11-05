# Aula Projeto Novo

Migração do backend do sistema de estacionamento para Python + Django, conforme
a documentação em `docs/roteiro-migracao.md`.

## Estado

O backend está em `backend-django/` e contém a configuração Django (Tarefa 1),
o app `api` com os models e migrations (Tarefa 2), o middleware CORS e os
pontos de entrada das views e do serviço. Os endpoints serão implementados nas
próximas etapas.

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
