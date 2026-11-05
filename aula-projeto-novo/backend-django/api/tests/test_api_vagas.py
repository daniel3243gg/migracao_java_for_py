"""Testes da spec api-vagas. Caminhos sem barra, como o frontend legado chama."""

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.tests.test_api_clientes import ApiTestCase


class ListarConsultarVagasTests(ApiTestCase):
    def test_vaga_inicial(self):
        a01 = Vaga.objects.get(numero="A01")
        resposta = self.client.get(f"/api/vagas/{a01.id}")
        self.assertEqual(resposta.json(), {"id": a01.id, "numero": "A01", "tipo": "CARRO", "status": "LIVRE"})

    def test_lista_ordenada_por_numero(self):
        Vaga.objects.create(numero="A00", tipo="MOTO")
        numeros = [v["numero"] for v in self.client.get("/api/vagas").json()]
        self.assertEqual(numeros[0], "A00")
        self.assertEqual(numeros, sorted(numeros))
        self.assertEqual(len(numeros), 16)

    def test_vagas_livres_para_formulario_de_entrada(self):
        Vaga.objects.filter(numero="A01").update(status="OCUPADA")
        numeros = [v["numero"] for v in self.client.get("/api/vagas?status=LIVRE").json()]
        self.assertNotIn("A01", numeros)
        self.assertEqual(numeros[0], "A02")
        self.assertEqual(len(numeros), 14)

    def test_filtro_vazio(self):
        self.assertEqual(len(self.client.get("/api/vagas?status=").json()), 15)

    def test_filtro_desconhecido(self):
        resposta = self.client.get("/api/vagas?status=livre")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [])

    def test_consulta_inexistente(self):
        self.assertErro(self.client.get("/api/vagas/999"), 404, "Vaga não encontrada")


class CadastrarVagaTests(ApiTestCase):
    def test_numero_obrigatorio(self):
        self.assertErro(self.post("/api/vagas", {"numero": " ", "tipo": "CARRO"}), 400, "Campo 'numero' é obrigatório")

    def test_tipo_minusculo(self):
        resposta = self.post("/api/vagas", {"numero": "C01", "tipo": "carro"})
        self.assertErro(resposta, 400, "Campo 'tipo' deve ser CARRO ou MOTO")

    def test_tipo_ausente(self):
        self.assertErro(self.post("/api/vagas", {"numero": "C01"}), 400, "Campo 'tipo' deve ser CARRO ou MOTO")

    def test_status_enviado_e_ignorado(self):
        resposta = self.post("/api/vagas", {"numero": "C01", "tipo": "CARRO", "status": "OCUPADA"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["status"], "LIVRE")

    def test_numero_gravado_como_recebido(self):
        self.assertEqual(self.post("/api/vagas", {"numero": "c01", "tipo": "MOTO"}).json()["numero"], "c01")

    def test_cadastro_repetido(self):
        resposta = self.post("/api/vagas", {"numero": "A01", "tipo": "CARRO"})
        self.assertErro(resposta, 409, "Número de vaga já cadastrado")


class EditarVagaTests(ApiTestCase):
    def setUp(self):
        self.a02 = Vaga.objects.get(numero="A02")

    def test_edicao_para_numero_de_outra(self):
        resposta = self.put(f"/api/vagas/{self.a02.id}", {"numero": "A01", "tipo": "CARRO"})
        self.assertErro(resposta, 409, "Número de vaga já cadastrado")

    def test_ocupacao_manual(self):
        resposta = self.put(f"/api/vagas/{self.a02.id}", {"numero": "A02", "tipo": "CARRO", "status": "OCUPADA"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["status"], "OCUPADA")

    def test_status_invalido_vira_livre(self):
        self.a02.status = "OCUPADA"
        self.a02.save()
        resposta = self.put(f"/api/vagas/{self.a02.id}", {"numero": "A02", "tipo": "CARRO", "status": "RESERVADA"})
        self.assertEqual(resposta.json()["status"], "LIVRE")

    def test_status_ausente_vira_livre(self):
        self.a02.status = "OCUPADA"
        self.a02.save()
        resposta = self.put(f"/api/vagas/{self.a02.id}", {"numero": "A02", "tipo": "MOTO"})
        self.assertEqual(resposta.json(), {"id": self.a02.id, "numero": "A02", "tipo": "MOTO", "status": "LIVRE"})

    def test_edicao_de_inexistente(self):
        self.assertErro(self.put("/api/vagas/999", {"numero": "Z9", "tipo": "CARRO"}), 404, "Vaga não encontrada")


class ExcluirVagaTests(ApiTestCase):
    def test_vaga_com_historico(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        veiculo = Veiculo.objects.create(placa="ABC1234", marca="F", modelo="U", cor="B", cliente=cliente)
        a01 = Vaga.objects.get(numero="A01")
        Permanencia.objects.create(veiculo=veiculo, vaga=a01)
        resposta = self.client.delete(f"/api/vagas/{a01.id}")
        self.assertErro(resposta, 409, "Não é possível excluir vaga com permanências registradas")

    def test_vaga_sem_historico(self):
        b05 = Vaga.objects.get(numero="B05")
        resposta = self.client.delete(f"/api/vagas/{b05.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"message": "Vaga excluída com sucesso"})

    def test_vaga_ocupada_sem_historico(self):
        b05 = Vaga.objects.get(numero="B05")
        b05.status = "OCUPADA"
        b05.save()
        self.assertEqual(self.client.delete(f"/api/vagas/{b05.id}").status_code, 200)

    def test_exclusao_de_inexistente(self):
        self.assertErro(self.client.delete("/api/vagas/999"), 404, "Vaga não encontrada")
