"""Testes do schema (spec modelo-de-dados da change fundacao-django-e-models)."""

import importlib
from datetime import datetime
from decimal import Decimal

from django.apps import apps as registro_atual
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo

seed_vagas = importlib.import_module("api.migrations.0002_seed_vagas")


def criar_cliente(cpf="111.111.111-11", nome="Ana"):
    return Cliente.objects.create(nome=nome, cpf=cpf)


def criar_veiculo(cliente, placa="ABC1234"):
    return Veiculo.objects.create(placa=placa, marca="Fiat", modelo="Uno", cor="Branco", cliente=cliente)


class ClienteTests(TestCase):
    def test_cliente_minimo_tem_opcionais_nulos(self):
        cliente = criar_cliente()
        cliente.refresh_from_db()
        self.assertIsNotNone(cliente.id)
        self.assertIsNone(cliente.telefone)
        self.assertIsNone(cliente.email)

    def test_cpf_repetido_e_rejeitado(self):
        criar_cliente()
        with self.assertRaises(IntegrityError), transaction.atomic():
            criar_cliente(nome="Bia")


class VeiculoTests(TestCase):
    def test_placa_repetida_e_rejeitada(self):
        cliente = criar_cliente()
        criar_veiculo(cliente)
        with self.assertRaises(IntegrityError), transaction.atomic():
            criar_veiculo(cliente)

    def test_cliente_inexistente_viola_fk(self):
        Veiculo.objects.create(placa="XYZ9999", marca="Fiat", modelo="Uno", cor="Preto", cliente_id=999999)
        with self.assertRaises(IntegrityError):
            connection.check_constraints(table_names=["veiculos"])
        Veiculo.objects.filter(placa="XYZ9999").delete()


class VagaTests(TestCase):
    def test_status_padrao_livre(self):
        vaga = Vaga.objects.create(numero="Z01", tipo=Vaga.Tipo.CARRO)
        vaga.refresh_from_db()
        self.assertEqual(vaga.status, "LIVRE")

    def test_numero_repetido_e_rejeitado(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vaga.objects.create(numero="A01", tipo="CARRO")

    def test_tipo_fora_do_dominio_e_rejeitado(self):
        for tipo in ["CAMINHAO", "carro"]:
            with self.subTest(tipo=tipo):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Vaga.objects.create(numero="Z02", tipo=tipo)

    def test_status_fora_do_dominio_e_rejeitado_na_criacao_e_na_atualizacao(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vaga.objects.create(numero="Z03", tipo="MOTO", status="RESERVADA")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vaga.objects.filter(numero="A01").update(status="RESERVADA")


class PermanenciaTests(TestCase):
    def setUp(self):
        self.veiculo = criar_veiculo(criar_cliente())
        self.vaga = Vaga.objects.get(numero="A01")

    def test_permanencia_recem_criada(self):
        antes = datetime.now()
        p = Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga)
        depois = datetime.now()
        p.refresh_from_db()
        self.assertEqual(p.status, "ABERTO")
        self.assertTrue(antes <= p.data_hora_entrada <= depois)
        self.assertIsNone(p.data_hora_entrada.tzinfo)
        self.assertIsNone(p.data_hora_saida)
        self.assertIsNone(p.valor_total)

    def test_entrada_explicita_e_preservada(self):
        entrada = datetime(2026, 1, 10, 8, 30, 15)
        p = Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga, data_hora_entrada=entrada)
        p.refresh_from_db()
        self.assertEqual(p.data_hora_entrada, entrada)

    def test_valor_monetario_exato(self):
        p = Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga, valor_total=Decimal("15.00"))
        p.refresh_from_db()
        self.assertIsInstance(p.valor_total, Decimal)
        self.assertEqual(str(p.valor_total), "15.00")

    def test_status_invalido_e_rejeitado(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga, status="CANCELADO")

    def test_banco_aceita_duas_abertas_para_o_mesmo_veiculo(self):
        Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga)
        Permanencia.objects.create(veiculo=self.veiculo, vaga=Vaga.objects.get(numero="A02"))
        self.assertEqual(Permanencia.objects.filter(veiculo=self.veiculo, status="ABERTO").count(), 2)


class ExclusaoTests(TestCase):
    def test_cliente_exclui_veiculos_sem_historico(self):
        cliente = criar_cliente()
        criar_veiculo(cliente, "AAA1111")
        criar_veiculo(cliente, "BBB2222")
        cliente.delete()
        self.assertFalse(Cliente.objects.exists())
        self.assertFalse(Veiculo.objects.exists())

    def test_veiculo_com_historico_nao_e_excluido(self):
        veiculo = criar_veiculo(criar_cliente())
        Permanencia.objects.create(
            veiculo=veiculo, vaga=Vaga.objects.get(numero="A01"), status="FINALIZADO"
        )
        with self.assertRaises(ProtectedError):
            veiculo.delete()
        self.assertTrue(Veiculo.objects.filter(pk=veiculo.pk).exists())

    def test_vaga_com_historico_nao_e_excluida(self):
        vaga = Vaga.objects.get(numero="A01")
        Permanencia.objects.create(veiculo=criar_veiculo(criar_cliente()), vaga=vaga)
        with self.assertRaises(ProtectedError):
            vaga.delete()
        self.assertTrue(Vaga.objects.filter(pk=vaga.pk).exists())

    def test_cliente_cujo_veiculo_tem_historico_nao_e_removido_parcialmente(self):
        cliente = criar_cliente()
        com_historico = criar_veiculo(cliente, "AAA1111")
        criar_veiculo(cliente, "BBB2222")
        Permanencia.objects.create(veiculo=com_historico, vaga=Vaga.objects.get(numero="A01"))
        with self.assertRaises(ProtectedError):
            cliente.delete()
        self.assertTrue(Cliente.objects.filter(pk=cliente.pk).exists())
        self.assertEqual(Veiculo.objects.filter(cliente=cliente).count(), 2)

    def test_vaga_ocupada_sem_historico_pode_ser_excluida(self):
        vaga = Vaga.objects.get(numero="A01")
        vaga.status = Vaga.Status.OCUPADA
        vaga.save()
        vaga.delete()
        self.assertFalse(Vaga.objects.filter(numero="A01").exists())


class VagasIniciaisTests(TestCase):
    def test_banco_novo_tem_15_vagas_livres(self):
        self.assertEqual(Vaga.objects.count(), 15)
        self.assertEqual(Vaga.objects.filter(tipo="CARRO").count(), 10)
        self.assertEqual(Vaga.objects.filter(tipo="MOTO").count(), 5)
        self.assertFalse(Vaga.objects.exclude(status="LIVRE").exists())
        esperado = [f"A{n:02d}" for n in range(1, 11)] + [f"B{n:02d}" for n in range(1, 6)]
        self.assertEqual([v.numero for v in Vaga.objects.order_by("numero")], esperado)
        self.assertFalse(Cliente.objects.exists())
        self.assertFalse(Veiculo.objects.exists())
        self.assertFalse(Permanencia.objects.exists())

    def test_reexecucao_nao_duplica(self):
        seed_vagas.criar_vagas_iniciais(registro_atual, None)
        self.assertEqual(Vaga.objects.count(), 15)

    def test_numero_existente_nao_e_sobrescrito(self):
        Vaga.objects.all().delete()
        Vaga.objects.create(numero="A01", tipo="MOTO", status="OCUPADA")
        seed_vagas.criar_vagas_iniciais(registro_atual, None)
        a01 = Vaga.objects.get(numero="A01")
        self.assertEqual((a01.tipo, a01.status), ("MOTO", "OCUPADA"))
        self.assertEqual(Vaga.objects.count(), 15)
