import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "estacionamento.settings")

# Ponto de entrada usado por Gunicorn, uWSGI ou outros servidores WSGI.
application = get_wsgi_application()
