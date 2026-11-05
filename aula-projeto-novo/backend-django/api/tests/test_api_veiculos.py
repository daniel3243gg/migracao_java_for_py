"""Testes da spec api-veiculos. Caminhos sem barra, como o frontend legado chama."""

from django.db import connection
from django.test.utils import CaptureQueriesContext

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.tests.test_api_clientes import ApiTestCase


def corpo(cliente_id, placa="ABC1234", **extra):
    dados = {"placa": placa, "marca": "Fiat", "modelo": "Uno", "cor": "Branco", "clienteId": cliente_id}
    dados.update(extra)
    return dados


class VeiculoBase(ApiTestCase):
    def setUp(self):
        self.ana = Cliente.objects.create(nome="Ana", cpf="111")
        self.bruno = Cliente.objects.create(nome="Bruno", cpf="222")

    def criar(self, placa, cliente=None):
        return Veiculo.objects.create(
            placa=placa, marca="Fiat", modelo="Uno", cor="Branco", cliente=cliente or self.ana
        )


class ListarConsultarVeiculosTests(VeiculoBase):
    def test_lista_ordenada_por_placa_com_nome_do_cliente(self):
        for placa in ["CCC3333", "AAA1111", "BBB2222"]:
            self.criar(placa)
        resposta = self.client.get("/api/veiculos")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual([v["placa"] for v in resposta.json()], ["AAA1111", "BBB2222", "CCC3333"])
        self.assertTrue(all(v["clienteNome"] == "Ana" for v in resposta.json()))

    def test_listagem_sem_n_mais_1(self):
        for placa in ["AAA1111", "BBB2222", "CCC3333"]:
            self.criar(placa, self.bruno)
        with CaptureQueriesContext(connection) as consultas:
            self.client.get("/api/veiculos")
        self.assertEqual(len(consultas), 1)

    def test_consulta_com_nome_do_cliente(self):
        veiculo = self.criar("ABC1234")
        corpo_resposta = self.client.get(f"/api/veiculos/{veiculo.id}").json()
        self.assertEqual(corpo_resposta["clienteNome"], "Ana")
        self.assertEqual(corpo_resposta["clienteId"], self.ana.id)

    def test_consulta_inexistente(self):
        self.assertErro(self.client.get("/api/veiculos/999"), 404, "Veículo não encontrado")


class CadastrarVeiculoTests(VeiculoBase):
    def test_cadastro_do_frontend(self):
        resposta = self.post("/api/veiculos", corpo(self.ana.id))
        self.assertEqual(resposta.status_code, 201)
        dados = resposta.json()
        self.assertIsInstance(dados["id"], int)
        self.assertEqual(dados["clienteNome"], "Ana")

    def test_placa_nao_convertida(self):
        resposta = self.post("/api/veiculos", corpo(self.ana.id, placa="abc1234"))
        self.assertEqual(resposta.json()["placa"], "abc1234")

    def test_cliente_id_texto_numerico_aceito(self):
        resposta = self.post("/api/veiculos", corpo(str(self.ana.id)))
        self.assertEqual(resposta.status_code, 201)

    def test_ordem_de_validacao(self):
        casos = [
            ({}, "placa"),
            ({"placa": "A"}, "marca"),
            ({"placa": "A", "marca": "M"}, "modelo"),
            ({"placa": "A", "marca": "M", "modelo": "X"}, "cor"),
            ({"placa": "A", "marca": "M", "modelo": "X", "cor": ""}, "cor"),
            ({"placa": "A", "marca": "M", "modelo": "X", "cor": "C"}, "clienteId"),
            ({"placa": "A", "marca": "M", "modelo": "X", "cor": "C", "clienteId": "x"}, "clienteId"),
        ]
        for dados, campo in casos:
            with self.subTest(campo=campo, dados=dados):
                self.assertErro(self.post("/api/veiculos", dados), 400, f"Campo '{campo}' é obrigatório")

    def test_cliente_inexistente(self):
        self.assertErro(self.post("/api/veiculos", corpo(999)), 404, "Cliente não encontrado")
        self.assertFalse(Veiculo.objects.exists())

    def test_placa_repetida(self):
        self.criar("ABC1234")
        self.assertErro(self.post("/api/veiculos", corpo(self.bruno.id)), 409, "Placa já cadastrada")

    def test_placa_repetida_vem_antes_de_cliente_inexistente(self):
        self.criar("ABC1234")
        self.assertErro(self.post("/api/veiculos", corpo(999)), 409, "Placa já cadastrada")


class EditarVeiculoTests(VeiculoBase):
    def setUp(self):
        super().setUp()
        self.v1 = self.criar("AAA1111")
        self.v2 = self.criar("BBB2222")

    def test_troca_de_cliente(self):
        resposta = self.put(f"/api/veiculos/{self.v1.id}", corpo(self.bruno.id, placa="AAA1111"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["clienteNome"], "Bruno")

    def test_placa_de_outro_veiculo(self):
        resposta = self.put(f"/api/veiculos/{self.v1.id}", corpo(self.ana.id, placa="BBB2222"))
        self.assertErro(resposta, 409, "Placa já cadastrada")

    def test_edicao_de_inexistente(self):
        self.assertErro(self.put("/api/veiculos/999", corpo(self.ana.id)), 404, "Veículo não encontrado")

    def test_edicao_com_cliente_inexistente(self):
        resposta = self.put(f"/api/veiculos/{self.v1.id}", corpo(999, placa="AAA1111"))
        self.assertErro(resposta, 404, "Cliente não encontrado")


class ExcluirVeiculoTests(VeiculoBase):
    def test_veiculo_com_permanencia_finalizada(self):
        veiculo = self.criar("ABC1234")
        Permanencia.objects.create(veiculo=veiculo, vaga=Vaga.objects.get(numero="A01"), status="FINALIZADO")
        resposta = self.client.delete(f"/api/veiculos/{veiculo.id}")
        self.assertErro(resposta, 409, "Não é possível excluir veículo com permanências registradas")
        self.assertTrue(Veiculo.objects.filter(pk=veiculo.pk).exists())

    def test_veiculo_sem_historico(self):
        veiculo = self.criar("ABC1234")
        resposta = self.client.delete(f"/api/veiculos/{veiculo.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"message": "Veículo excluído com sucesso"})

    def test_exclusao_de_inexistente(self):
        self.assertErro(self.client.delete("/api/veiculos/999"), 404, "Veículo não encontrado")
