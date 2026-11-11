"""Regras de entrada e saída do estacionamento (Tarefa 5 do roteiro).

Equivalente ao PermanenciaService do legado. As regras violadas levantam
ValueError, que a view converte em HTTP 409. Recurso inexistente levanta
NaoEncontrado (subclasse de ValueError), que a view converte em HTTP 404,
como o IllegalArgumentException do Java.
"""

import math
from datetime import datetime
from decimal import Decimal

from django.db import transaction

from ..models import Permanencia, Vaga, Veiculo

TARIFA_POR_HORA = Decimal("5.00")


class NaoEncontrado(ValueError):
    """Veículo, vaga ou permanência inexistente (HTTP 404)."""


def registrar_entrada(veiculo_id, vaga_id):
    # atomic substitui o setAutoCommit(false)/commit/rollback do JDBC: a vaga
    # ocupada e a permanência criada são gravadas juntas ou nenhuma é gravada.
    with transaction.atomic():
        # 1. Veículo já estacionado?
        if Permanencia.objects.filter(veiculo_id=veiculo_id, status=Permanencia.Status.ABERTO).exists():
            raise ValueError("Veículo já possui uma permanência em aberto.")

        # No Java o veículo inexistente estourava a FK e virava 500;
        # a Tarefa 8 pede 404 para recurso inexistente.
        if not Veiculo.objects.filter(id=veiculo_id).exists():
            raise NaoEncontrado("Veículo não encontrado.")

        # 2. Vaga existe e está livre? (select_for_update = SELECT ... FOR UPDATE do legado)
        try:
            vaga = Vaga.objects.select_for_update().get(id=vaga_id)
        except Vaga.DoesNotExist:
            raise NaoEncontrado("Vaga não encontrada.")
        if vaga.status != Vaga.Status.LIVRE:
            raise ValueError("Vaga já está ocupada.")

        # 3. Ocupa a vaga
        vaga.status = Vaga.Status.OCUPADA
        vaga.save()

        # 4. Abre a permanência
        permanencia = Permanencia.objects.create(
            veiculo_id=veiculo_id,
            vaga=vaga,
            data_hora_entrada=datetime.now(),
            status=Permanencia.Status.ABERTO,
        )

    return Permanencia.objects.select_related("veiculo", "vaga").get(id=permanencia.id)


def registrar_saida(permanencia_id):
    with transaction.atomic():
        # 1. Permanência existe e está aberta?
        try:
            permanencia = (
                Permanencia.objects.select_for_update()
                .select_related("veiculo", "vaga")
                .get(id=permanencia_id)
            )
        except Permanencia.DoesNotExist:
            raise NaoEncontrado("Permanência não encontrada.")
        if permanencia.status != Permanencia.Status.ABERTO:
            raise ValueError("Permanência já foi finalizada.")

        # 2. Calcula o valor
        saida = datetime.now()
        valor = _calcular_valor(permanencia.data_hora_entrada, saida)

        # 3. Finaliza a permanência
        permanencia.data_hora_saida = saida
        permanencia.valor_total = valor
        permanencia.status = Permanencia.Status.FINALIZADO
        permanencia.save()

        # 4. Libera a vaga
        vaga = permanencia.vaga
        vaga.status = Vaga.Status.LIVRE
        vaga.save()

    return permanencia


def _calcular_valor(entrada, saida):
    """R$ 5,00 por hora, frações arredondadas para cima, mínimo de 1 hora.

    Como o ChronoUnit.MINUTES.between do Java, conta só minutos inteiros
    (os segundos são descartados antes de arredondar).
    """
    minutos = int((saida - entrada).total_seconds() // 60)
    horas = max(1, math.ceil(minutos / 60))
    return TARIFA_POR_HORA * horas
