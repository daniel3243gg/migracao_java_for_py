"""Testes da spec api-clientes. Caminhos sem barra, como o frontend legado chama."""

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class ApiTestCase(TestCase):
    def post(self, url, dados):
        return self.client.post(url, data=dados, content_type="application/json")

    def put(self, url, dados):
        return self.client.put(url, data=dados, content_type="application/json")

    def assertErro(self, resposta, status, mensagem):
        self.assertEqual(resposta.status_code, status, resposta.content)
        self.assertEqual(resposta.json(), {"error": mensagem})


class ListarConsultarClientesTests(ApiTestCase):
    def test_lista_ordenada_por_nome(self):
        for i, nome in enumerate(["Carlos", "Ana", "Bruno"]):
            Cliente.objects.create(nome=nome, cpf=str(i))
        resposta = self.client.get("/api/clientes")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual([c["nome"] for c in resposta.json()], ["Ana", "Bruno", "Carlos"])

    def test_cliente_sem_opcionais(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        resposta = self.client.get(f"/api/clientes/{cliente.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            {"id": cliente.id, "nome": "Ana", "cpf": "111", "telefone": None, "email": None},
        )

    def test_consulta_inexistente(self):
        self.assertErro(self.client.get("/api/clientes/999"), 404, "Cliente não encontrado")


class CadastrarClienteTests(ApiTestCase):
    def test_cadastro_do_frontend(self):
        resposta = self.post(
            "/api/clientes",
            {"nome": "Ana", "cpf": "111.111.111-11", "telefone": "", "email": ""},
        )
        self.assertEqual(resposta.status_code, 201)
        corpo = resposta.json()
        self.assertIsInstance(corpo["id"], int)
        self.assertEqual(corpo["telefone"], "")
        self.assertEqual(corpo["email"], "")
        self.assertTrue(Cliente.objects.filter(cpf="111.111.111-11").exists())

    def test_valores_gravados_como_recebidos(self):
        resposta = self.post("/api/clientes", {"nome": "  Ana  ", "cpf": "111"})
        self.assertEqual(resposta.json()["nome"], "  Ana  ")

    def test_nome_so_com_espacos(self):
        self.assertErro(self.post("/api/clientes", {"nome": "   ", "cpf": "123"}), 400, "Campo 'nome' é obrigatório")

    def test_nome_validado_antes_do_cpf(self):
        self.assertErro(self.post("/api/clientes", {}), 400, "Campo 'nome' é obrigatório")

    def test_cpf_obrigatorio(self):
        self.assertErro(self.post("/api/clientes", {"nome": "Ana", "cpf": ""}), 400, "Campo 'cpf' é obrigatório")

    def test_nome_numerico_rejeitado(self):
        self.assertErro(self.post("/api/clientes", {"nome": 123, "cpf": "1"}), 400, "Campo 'nome' é obrigatório")

    def test_cpf_repetido(self):
        Cliente.objects.create(nome="Ana", cpf="111")
        self.assertErro(self.post("/api/clientes", {"nome": "Bia", "cpf": "111"}), 409, "CPF já cadastrado")
        self.assertEqual(Cliente.objects.count(), 1)


class EditarClienteTests(ApiTestCase):
    def setUp(self):
        self.c1 = Cliente.objects.create(nome="Ana", cpf="111", telefone="(11) 9999")
        self.c2 = Cliente.objects.create(nome="Bia", cpf="222")

    def test_edicao_para_cpf_de_outro(self):
        resposta = self.put(f"/api/clientes/{self.c1.id}", {"nome": "Ana", "cpf": "222"})
        self.assertErro(resposta, 409, "CPF já cadastrado")
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.cpf, "111")

    def test_edicao_mantendo_proprio_cpf(self):
        resposta = self.put(f"/api/clientes/{self.c1.id}", {"nome": "Ana Maria", "cpf": "111"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["nome"], "Ana Maria")

    def test_opcional_omitido_vira_null(self):
        resposta = self.put(f"/api/clientes/{self.c1.id}", {"nome": "Ana", "cpf": "111"})
        self.assertIsNone(resposta.json()["telefone"])
        self.c1.refresh_from_db()
        self.assertIsNone(self.c1.telefone)

    def test_edicao_de_inexistente(self):
        self.assertErro(self.put("/api/clientes/999", {"nome": "X", "cpf": "9"}), 404, "Cliente não encontrado")

    def test_validacao_antes_da_existencia(self):
        self.assertErro(self.put("/api/clientes/999", {"cpf": "9"}), 400, "Campo 'nome' é obrigatório")


class ExcluirClienteTests(ApiTestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Ana", cpf="111")
        self.veiculo = Veiculo.objects.create(
            placa="ABC1234", marca="Fiat", modelo="Uno", cor="Branco", cliente=self.cliente
        )

    def test_cliente_com_veiculo_sem_historico(self):
        resposta = self.client.delete(f"/api/clientes/{self.cliente.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"message": "Cliente excluído com sucesso"})
        self.assertFalse(Veiculo.objects.filter(pk=self.veiculo.pk).exists())

    def test_cliente_com_veiculo_com_historico(self):
        Permanencia.objects.create(veiculo=self.veiculo, vaga=Vaga.objects.get(numero="A01"))
        resposta = self.client.delete(f"/api/clientes/{self.cliente.id}")
        self.assertErro(resposta, 409, "Não é possível excluir cliente com veículos cadastrados")
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
        self.assertTrue(Veiculo.objects.filter(pk=self.veiculo.pk).exists())

    def test_exclusao_de_inexistente(self):
        self.assertErro(self.client.delete("/api/clientes/999"), 404, "Cliente não encontrado")
