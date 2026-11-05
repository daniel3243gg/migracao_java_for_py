"""Testes de configuração (spec configuracao-backend da change fundacao-django-e-models)."""

import importlib
import os
from datetime import datetime
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.db import connection
from django.test import Client, TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo

import estacionamento.settings as modulo_settings


class DependenciasTests(TestCase):
    def test_requirements_so_tem_django(self):
        linhas = [
            linha.strip()
            for linha in (Path(settings.BASE_DIR) / "requirements.txt").read_text().splitlines()
            if linha.strip() and not linha.strip().startswith("#")
        ]
        self.assertEqual(len(linhas), 1)
        self.assertTrue(linhas[0].lower().startswith("django"))
        for driver in ["psycopg", "mysqlclient", "pymysql", "oracledb"]:
            self.assertNotIn(driver, linhas[0].lower())


class BancoTests(TestCase):
    def _recarregar_settings(self, env):
        with mock.patch.dict(os.environ, env, clear=False):
            if "DB_PATH" not in env:
                os.environ.pop("DB_PATH", None)
            importlib.reload(modulo_settings)
            nome = modulo_settings.DATABASES["default"]["NAME"]
        importlib.reload(modulo_settings)
        return modulo_settings.DATABASES["default"], nome

    def test_sem_db_path_usa_db_sqlite3_na_raiz(self):
        config, nome = self._recarregar_settings({})
        self.assertEqual(config["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(Path(nome), Path(settings.BASE_DIR) / "db.sqlite3")

    def test_db_path_e_respeitado(self):
        _, nome = self._recarregar_settings({"DB_PATH": "/app/data/db.sqlite3"})
        self.assertEqual(nome, "/app/data/db.sqlite3")

    def test_apenas_tabelas_do_dominio(self):
        tabelas = set(connection.introspection.table_names())
        self.assertEqual(
            tabelas,
            {"clientes", "veiculos", "vagas", "permanencias", "django_migrations", "django_content_type"},
        )


class DatasTests(TestCase):
    def test_use_tz_desligado_e_data_ingenua(self):
        self.assertFalse(settings.USE_TZ)
        cliente = Cliente.objects.create(nome="Ana", cpf="1")
        veiculo = Veiculo.objects.create(placa="A", marca="M", modelo="X", cor="C", cliente=cliente)
        entrada = datetime(2026, 3, 1, 14, 5, 9, 123456)
        p = Permanencia.objects.create(veiculo=veiculo, vaga=Vaga.objects.first(), data_hora_entrada=entrada)
        p.refresh_from_db()
        self.assertIsNone(p.data_hora_entrada.tzinfo)
        self.assertEqual(p.data_hora_entrada, entrada)


class HttpTests(TestCase):
    def test_post_sem_token_csrf_nao_e_barrado(self):
        client = Client(enforce_csrf_checks=True)
        resposta = client.post("/api/clientes", data={"nome": "Ana"}, content_type="application/json")
        self.assertNotEqual(resposta.status_code, 403)

    def test_sem_apps_de_auth_e_sessao(self):
        for app in ["django.contrib.auth", "django.contrib.sessions", "django.contrib.messages", "django.contrib.admin"]:
            self.assertNotIn(app, settings.INSTALLED_APPS)
        self.assertNotIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)

    def test_host_do_proxy_e_aceito(self):
        resposta = Client().get("/health", HTTP_HOST="backend:8080")
        self.assertEqual(resposta.status_code, 200)

    def test_rota_inexistente_sem_barra_nao_redireciona(self):
        resposta = Client().get("/api/inexistente")
        self.assertNotIn(resposta.status_code, (301, 302))
