"""Testes da spec api-dashboard."""

from api.models import Vaga
from api.tests.test_api_clientes import ApiTestCase


class DashboardTests(ApiTestCase):
    def test_banco_recem_migrado(self):
        resposta = self.client.get("/api/dashboard")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            {"totalVagas": 15, "vagasLivres": 15, "vagasOcupadas": 0, "veiculosEstacionados": 0},
        )

    def test_ocupacao_manual_sem_permanencia(self):
        a01 = Vaga.objects.get(numero="A01")
        self.put(f"/api/vagas/{a01.id}", {"numero": "A01", "tipo": "CARRO", "status": "OCUPADA"})
        dados = self.client.get("/api/dashboard").json()
        self.assertEqual(dados["vagasOcupadas"], 1)
        self.assertEqual(dados["vagasLivres"], 14)
        self.assertEqual(dados["veiculosEstacionados"], 0)

    def test_sem_vagas(self):
        Vaga.objects.all().delete()
        self.assertEqual(
            self.client.get("/api/dashboard").json(),
            {"totalVagas": 0, "vagasLivres": 0, "vagasOcupadas": 0, "veiculosEstacionados": 0},
        )

    def test_post_no_dashboard(self):
        self.assertErro(self.client.post("/api/dashboard"), 405, "Método não permitido")
