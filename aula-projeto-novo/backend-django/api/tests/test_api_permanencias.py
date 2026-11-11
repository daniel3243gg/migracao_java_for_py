"""Testes das Tarefas 5 e 8: entrada, saída, cálculo e validações de permanência."""

from datetime import datetime, timedelta
from decimal import Decimal

from django.test import SimpleTestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.services.permanencia_service import _calcular_valor
from api.tests.test_api_clientes import ApiTestCase


class CalculoValorTests(SimpleTestCase):
    def _valor(self, **duracao):
        entrada = datetime(2026, 1, 1, 8, 0, 0)
        return _calcular_valor(entrada, entrada + timedelta(**duracao))

    def test_minimo_uma_hora(self):
        self.assertEqual(self._valor(minutes=0), Decimal("5.00"))
        self.assertEqual(self._valor(minutes=59), Decimal("5.00"))

    def test_hora_exata(self):
        self.assertEqual(self._valor(minutes=60), Decimal("5.00"))

    def test_fracao_arredonda_para_cima(self):
        self.assertEqual(self._valor(minutes=61), Decimal("10.00"))
        self.assertEqual(self._valor(minutes=120), Decimal("10.00"))
        self.assertEqual(self._valor(minutes=121), Decimal("15.00"))

    def test_segundos_descartados_como_no_java(self):
        self.assertEqual(self._valor(minutes=60, seconds=59), Decimal("5.00"))

    def test_resultado_decimal(self):
        self.assertIsInstance(self._valor(hours=3), Decimal)


class PermanenciaBase(ApiTestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        self.veiculo = Veiculo.objects.create(placa="ABC1234", marca="Fiat", modelo="Uno", cor="Prata", cliente=cliente)
        self.vaga = Vaga.objects.get(numero="A01")

    def entrar(self, veiculo_id=None, vaga_id=None):
        return self.post(
            "/api/permanencias/entrada",
            {"veiculoId": veiculo_id or self.veiculo.id, "vagaId": vaga_id or self.vaga.id},
        )


class EntradaTests(PermanenciaBase):
    def test_entrada_ocupa_vaga_e_abre_permanencia(self):
        resposta = self.entrar()
        self.assertEqual(resposta.status_code, 201, resposta.content)
        corpo = resposta.json()
        self.assertEqual(corpo["status"], "ABERTO")
        self.assertEqual(corpo["veiculoPlaca"], "ABC1234")
        self.assertEqual(corpo["veiculoModelo"], "Uno")
        self.assertEqual(corpo["vagaNumero"], "A01")
        self.assertIsNone(corpo["dataHoraSaida"])
        self.assertIsNone(corpo["valorTotal"])
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "OCUPADA")

    def test_rota_com_barra_final(self):
        resposta = self.post("/api/permanencias/entrada/", {"veiculoId": self.veiculo.id, "vagaId": self.vaga.id})
        self.assertEqual(resposta.status_code, 201)

    def test_ids_como_texto_numerico(self):
        resposta = self.post("/api/permanencias/entrada", {"veiculoId": str(self.veiculo.id), "vagaId": str(self.vaga.id)})
        self.assertEqual(resposta.status_code, 201)

    def test_campos_obrigatorios(self):
        mensagem = "Campos 'veiculoId' e 'vagaId' são obrigatórios"
        self.assertErro(self.post("/api/permanencias/entrada", {}), 400, mensagem)
        self.assertErro(self.post("/api/permanencias/entrada", {"veiculoId": self.veiculo.id}), 400, mensagem)
        self.assertErro(self.post("/api/permanencias/entrada", {"vagaId": self.vaga.id}), 400, mensagem)
        self.assertErro(self.post("/api/permanencias/entrada", {"veiculoId": None, "vagaId": self.vaga.id}), 400, mensagem)
        self.assertErro(self.post("/api/permanencias/entrada", {"veiculoId": "x", "vagaId": self.vaga.id}), 400, mensagem)

    def test_json_invalido(self):
        resposta = self.client.post("/api/permanencias/entrada", data="{", content_type="application/json")
        self.assertErro(resposta, 400, "JSON inválido")

    def test_veiculo_ja_estacionado(self):
        self.entrar()
        outra = Vaga.objects.get(numero="A02")
        self.assertErro(self.entrar(vaga_id=outra.id), 409, "Veículo já possui uma permanência em aberto.")
        outra.refresh_from_db()
        self.assertEqual(outra.status, "LIVRE")

    def test_vaga_ocupada(self):
        self.entrar()
        cliente = Cliente.objects.create(nome="Bia", cpf="222")
        outro = Veiculo.objects.create(placa="XYZ9876", marca="VW", modelo="Gol", cor="Preto", cliente=cliente)
        self.assertErro(self.entrar(veiculo_id=outro.id), 409, "Vaga já está ocupada.")
        self.assertEqual(Permanencia.objects.count(), 1)

    def test_vaga_inexistente(self):
        self.assertErro(self.entrar(vaga_id=9999), 404, "Vaga não encontrada.")
        self.assertEqual(Permanencia.objects.count(), 0)

    def test_veiculo_inexistente(self):
        self.assertErro(self.entrar(veiculo_id=9999), 404, "Veículo não encontrado.")
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "LIVRE")

    def test_metodo_errado(self):
        self.assertErro(self.client.get("/api/permanencias/entrada"), 405, "Método não permitido")


class SaidaTests(PermanenciaBase):
    def test_saida_finaliza_calcula_e_libera(self):
        pid = self.entrar().json()["id"]
        Permanencia.objects.filter(pk=pid).update(data_hora_entrada=datetime.now() - timedelta(minutes=90))
        resposta = self.client.put(f"/api/permanencias/{pid}/saida")
        self.assertEqual(resposta.status_code, 200, resposta.content)
        corpo = resposta.json()
        self.assertEqual(corpo["status"], "FINALIZADO")
        self.assertEqual(corpo["valorTotal"], 10.0)
        self.assertIsNotNone(corpo["dataHoraSaida"])
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "LIVRE")
        self.assertEqual(Permanencia.objects.get(pk=pid).valor_total, Decimal("10.00"))

    def test_saida_imediata_cobra_minimo(self):
        pid = self.entrar().json()["id"]
        self.assertEqual(self.client.put(f"/api/permanencias/{pid}/saida").json()["valorTotal"], 5.0)

    def test_saida_repetida(self):
        pid = self.entrar().json()["id"]
        self.client.put(f"/api/permanencias/{pid}/saida")
        self.assertErro(self.client.put(f"/api/permanencias/{pid}/saida"), 409, "Permanência já foi finalizada.")

    def test_saida_inexistente(self):
        self.assertErro(self.client.put("/api/permanencias/9999/saida"), 404, "Permanência não encontrada.")

    def test_veiculo_pode_voltar_depois_da_saida(self):
        pid = self.entrar().json()["id"]
        self.client.put(f"/api/permanencias/{pid}/saida")
        self.assertEqual(self.entrar().status_code, 201)

    def test_metodo_errado(self):
        self.assertErro(self.client.post("/api/permanencias/1/saida"), 405, "Método não permitido")


class ListaPermanenciasTests(PermanenciaBase):
    def test_filtros_e_ordem(self):
        primeira = self.entrar().json()["id"]
        Permanencia.objects.filter(pk=primeira).update(data_hora_entrada=datetime.now() - timedelta(hours=2))
        self.client.put(f"/api/permanencias/{primeira}/saida")
        segunda = self.entrar().json()["id"]

        todas = self.client.get("/api/permanencias").json()
        self.assertEqual([p["id"] for p in todas], [segunda, primeira])
        self.assertEqual([p["id"] for p in self.client.get("/api/permanencias?status=ABERTO").json()], [segunda])
        self.assertEqual([p["id"] for p in self.client.get("/api/permanencias?status=FINALIZADO").json()], [primeira])
        self.assertEqual(len(self.client.get("/api/permanencias?status=").json()), 2)

    def test_dashboard_reflete_entrada(self):
        self.entrar()
        dados = self.client.get("/api/dashboard").json()
        self.assertEqual(dados["vagasOcupadas"], 1)
        self.assertEqual(dados["veiculosEstacionados"], 1)
