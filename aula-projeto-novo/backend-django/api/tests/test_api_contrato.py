"""Testes da spec contrato-http-api (change views-cadastros-e-dashboard)."""

import json
from unittest import mock

from django.db import DatabaseError
from django.test import RequestFactory, SimpleTestCase, TestCase

from api.models import Cliente

from api.views.comum import (
    CorpoInvalido,
    converter_id,
    converter_inteiro,
    erro,
    ler_json,
    responder,
    texto_preenchido,
    tratar_erro_banco,
)


class ComumTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def _post(self, corpo):
        return self.rf.post("/x", data=corpo, content_type="application/json")

    def test_ler_json_objeto(self):
        self.assertEqual(ler_json(self._post('{"nome": "Ana"}')), {"nome": "Ana"})

    def test_ler_json_malformado(self):
        with self.assertRaises(CorpoInvalido):
            ler_json(self._post("{nome:"))

    def test_ler_json_lista(self):
        with self.assertRaises(CorpoInvalido):
            ler_json(self._post("[1, 2]"))

    def test_ler_json_vazio(self):
        with self.assertRaises(CorpoInvalido):
            ler_json(self._post(""))

    def test_converter_id(self):
        self.assertEqual(converter_id("12"), 12)
        self.assertIsNone(converter_id("abc"))
        self.assertIsNone(converter_id("1.5"))

    def test_converter_inteiro(self):
        self.assertEqual(converter_inteiro(12), 12)
        self.assertEqual(converter_inteiro("12"), 12)
        for invalido in [True, False, "1a", 1.5, "", None, "²", {"a": 1}]:
            with self.subTest(valor=invalido):
                self.assertIsNone(converter_inteiro(invalido))

    def test_texto_preenchido(self):
        self.assertTrue(texto_preenchido("Ana"))
        for invalido in ["", "   ", None, 123, ["a"]]:
            with self.subTest(valor=invalido):
                self.assertFalse(texto_preenchido(invalido))

    def test_erro_formato(self):
        resposta = erro("Campo 'nome' é obrigatório", 400)
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(json.loads(resposta.content), {"error": "Campo 'nome' é obrigatório"})

    def test_responder_utf8_sem_escape(self):
        resposta = responder({"m": "Veículo"})
        self.assertEqual(resposta["Content-Type"], "application/json; charset=UTF-8")
        self.assertIn("Veículo".encode("utf-8"), resposta.content)

    def test_responder_lista(self):
        self.assertEqual(json.loads(responder([]).content), [])

    def test_tratar_erro_banco(self):
        @tratar_erro_banco
        def quebra(request):
            raise DatabaseError("disco cheio")

        resposta = quebra(self.rf.get("/x"))
        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(json.loads(resposta.content), {"error": "Erro no banco de dados: disco cheio"})


class RotasTests(SimpleTestCase):
    def test_rotas_com_e_sem_barra(self):
        from django.urls import resolve

        from api.views import cliente_views, permanencia_views

        casos = [
            ("/api/clientes", cliente_views.lista_clientes, {}),
            ("/api/clientes/", cliente_views.lista_clientes, {}),
            ("/api/clientes/abc", cliente_views.detalhe_cliente, {"cliente_id": "abc"}),
            ("/api/clientes/7/", cliente_views.detalhe_cliente, {"cliente_id": "7"}),
            ("/api/permanencias/entrada/", permanencia_views.entrada, {}),
            ("/api/permanencias/5/saida", permanencia_views.saida, {"permanencia_id": 5}),
            ("/api/permanencias/5/saida/", permanencia_views.saida, {"permanencia_id": 5}),
        ]
        for caminho, view, kwargs in casos:
            with self.subTest(caminho=caminho):
                encontrado = resolve(caminho)
                self.assertIs(encontrado.func, view)
                self.assertEqual(encontrado.kwargs, kwargs)


class ContratoHttpTests(TestCase):
    def post(self, url, corpo):
        return self.client.post(url, data=corpo, content_type="application/json")

    def assertErro(self, resposta, status, mensagem):
        self.assertEqual(resposta.status_code, status, resposta.content)
        self.assertEqual(resposta.json(), {"error": mensagem})

    def test_post_com_e_sem_barra(self):
        sem = self.post("/api/clientes", {"nome": "Ana", "cpf": "1"})
        com = self.post("/api/clientes/", {"nome": "Bia", "cpf": "2"})
        self.assertEqual((sem.status_code, com.status_code), (201, 201))
        self.assertEqual(set(sem.json()), set(com.json()))

    def test_lista_com_e_sem_barra_iguais(self):
        self.assertEqual(self.client.get("/api/vagas").json(), self.client.get("/api/vagas/").json())

    def test_id_invalido(self):
        self.assertErro(self.client.get("/api/clientes/abc"), 400, "ID inválido")

    def test_delete_sem_id(self):
        self.assertErro(self.client.delete("/api/vagas"), 400, "ID obrigatório")

    def test_put_sem_id(self):
        self.assertErro(self.client.put("/api/veiculos", data={}, content_type="application/json"), 400, "ID obrigatório")

    def test_patch_em_colecao(self):
        self.assertErro(self.client.patch("/api/clientes"), 405, "Método não permitido")

    def test_post_em_item_nao_cria(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="1")
        self.assertErro(self.post(f"/api/clientes/{cliente.id}", {"nome": "Bia", "cpf": "2"}), 405, "Método não permitido")
        self.assertEqual(Cliente.objects.count(), 1)

    def test_json_malformado(self):
        self.assertErro(self.post("/api/clientes", "{nome:"), 400, "JSON inválido")

    def test_json_que_nao_e_objeto(self):
        self.assertErro(self.post("/api/vagas", "[1, 2]"), 400, "JSON inválido")

    def test_campo_extra_ignorado(self):
        resposta = self.post("/api/clientes", {"nome": "Ana", "cpf": "1", "apelido": "Aninha"})
        self.assertEqual(resposta.status_code, 201)
        self.assertNotIn("apelido", resposta.json())

    def test_lista_vazia(self):
        resposta = self.client.get("/api/clientes")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [])

    def test_utf8_sem_escape(self):
        resposta = self.client.get("/api/veiculos/999")
        self.assertEqual(resposta["Content-Type"], "application/json; charset=UTF-8")
        self.assertIn("Veículo não encontrado".encode("utf-8"), resposta.content)

    def test_cors_em_resposta_de_erro(self):
        self.assertEqual(self.client.get("/api/clientes/999")["Access-Control-Allow-Origin"], "*")

    def test_erro_de_banco(self):
        with mock.patch.object(Cliente.objects, "order_by", side_effect=DatabaseError("tabela travada")):
            resposta = self.client.get("/api/clientes")
        self.assertErro(resposta, 500, "Erro no banco de dados: tabela travada")
