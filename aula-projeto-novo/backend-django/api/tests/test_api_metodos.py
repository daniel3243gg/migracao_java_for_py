"""Confere a matriz de métodos HTTP dos endpoints de cadastro."""

from django.test import TestCase


class MatrizMetodosHttpTests(TestCase):
    colecoes = ("clientes", "veiculos", "vagas")

    def json_request(self, method, path):
        return getattr(self.client, method)(path, data="{}", content_type="application/json")

    def test_put_e_delete_em_colecao_exigem_id(self):
        for recurso in self.colecoes:
            for metodo in ("put", "delete"):
                with self.subTest(recurso=recurso, metodo=metodo):
                    resposta = self.json_request(metodo, f"/api/{recurso}")
                    self.assertEqual(resposta.status_code, 400, resposta.content)
                    self.assertEqual(resposta.json(), {"error": "ID obrigatório"})

    def test_metodos_nao_permitidos_em_colecao(self):
        for recurso in self.colecoes:
            resposta = self.json_request("patch", f"/api/{recurso}")
            with self.subTest(recurso=recurso):
                self.assertEqual(resposta.status_code, 405, resposta.content)
                self.assertEqual(resposta.json(), {"error": "Método não permitido"})

    def test_metodos_nao_permitidos_em_item(self):
        for recurso in self.colecoes:
            for metodo in ("post", "patch"):
                with self.subTest(recurso=recurso, metodo=metodo):
                    resposta = self.json_request(metodo, f"/api/{recurso}/1")
                    self.assertEqual(resposta.status_code, 405, resposta.content)
                    self.assertEqual(resposta.json(), {"error": "Método não permitido"})

