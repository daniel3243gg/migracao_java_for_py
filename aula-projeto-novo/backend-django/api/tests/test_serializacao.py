"""Testes de api/serializacao.py (Tarefa 4 do roteiro)."""

import json
from datetime import datetime
from decimal import Decimal

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.serializacao import (
    cliente_to_dict,
    permanencia_to_dict,
    vaga_to_dict,
    veiculo_to_dict,
)


class SerializacaoTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Ana", cpf="111")
        self.veiculo = Veiculo.objects.create(
            placa="ABC1234", marca="Fiat", modelo="Uno", cor="Branco", cliente=self.cliente
        )
        self.vaga = Vaga.objects.get(numero="A01")

    def test_cliente(self):
        self.assertEqual(
            cliente_to_dict(self.cliente),
            {"id": self.cliente.id, "nome": "Ana", "cpf": "111", "telefone": None, "email": None},
        )

    def test_veiculo_com_nome_do_cliente(self):
        veiculo = Veiculo.objects.select_related("cliente").get(pk=self.veiculo.pk)
        self.assertEqual(
            veiculo_to_dict(veiculo),
            {
                "id": veiculo.id,
                "placa": "ABC1234",
                "marca": "Fiat",
                "modelo": "Uno",
                "cor": "Branco",
                "clienteId": self.cliente.id,
                "clienteNome": "Ana",
            },
        )

    def test_vaga(self):
        self.assertEqual(
            vaga_to_dict(self.vaga),
            {"id": self.vaga.id, "numero": "A01", "tipo": "CARRO", "status": "LIVRE"},
        )

    def test_permanencia_aberta(self):
        entrada = datetime(2026, 3, 1, 14, 5, 9)
        p = Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga, data_hora_entrada=entrada)
        p = Permanencia.objects.select_related("veiculo", "vaga").get(pk=p.pk)
        self.assertEqual(
            permanencia_to_dict(p),
            {
                "id": p.id,
                "veiculoId": self.veiculo.id,
                "veiculoPlaca": "ABC1234",
                "veiculoModelo": "Uno",
                "vagaId": self.vaga.id,
                "vagaNumero": "A01",
                "dataHoraEntrada": "2026-03-01T14:05:09",
                "dataHoraSaida": None,
                "valorTotal": None,
                "status": "ABERTO",
            },
        )

    def test_permanencia_finalizada_valor_numerico(self):
        p = Permanencia.objects.create(
            veiculo=self.veiculo,
            vaga=self.vaga,
            data_hora_entrada=datetime(2026, 3, 1, 14, 0),
            data_hora_saida=datetime(2026, 3, 1, 16, 30, 0, 250000),
            valor_total=Decimal("15.00"),
            status="FINALIZADO",
        )
        p.refresh_from_db()
        dados = permanencia_to_dict(p)
        self.assertEqual(dados["dataHoraSaida"], "2026-03-01T16:30:00.250000")
        self.assertEqual(dados["valorTotal"], 15.0)
        # Número JSON, não texto.
        self.assertIn('"valorTotal": 15.0', json.dumps(dados))
