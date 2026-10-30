# Aula Projeto Novo

Migração do backend do sistema de estacionamento para Python + Django, conforme
a documentação em `docs/roteiro-migracao.md`.

## Estrutura inicial

O backend está em `backend-django/` e já contém a configuração Django, o app
`api`, os modelos, a migration inicial, o middleware CORS e os pontos de entrada
das views/serviços. Os endpoints serão implementados nas próximas etapas.

## Desenvolvimento local

```bash
cd backend-django
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8080
```

O banco local será criado como `backend-django/db.sqlite3`.
