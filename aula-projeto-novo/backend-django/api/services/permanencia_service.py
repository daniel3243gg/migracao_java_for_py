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


def registrar_entrada(veiculo_id, vaga_id, data_hora_entrada=None):
    """Registra uma entrada usando o horário informado ou o horário atual.

    ``data_hora_entrada`` é opcional para manter compatibilidade com o
    frontend existente. Quando informado, já deve ser um ``datetime`` válido;
    a conversão do JSON acontece na view.
    """
    with transaction.atomic():
        if Permanencia.objects.filter(veiculo_id=veiculo_id, status=Permanencia.Status.ABERTO).exists():
            raise ValueError("Veículo já possui uma permanência em aberto.")

        if not Veiculo.objects.filter(id=veiculo_id).exists():
            raise NaoEncontrado("Veículo não encontrado.")

        try:
            vaga = Vaga.objects.select_for_update().get(id=vaga_id)
        except Vaga.DoesNotExist:
            raise NaoEncontrado("Vaga não encontrada.")
        if vaga.status != Vaga.Status.LIVRE:
            raise ValueError("Vaga já está ocupada.")

        vaga.status = Vaga.Status.OCUPADA
        vaga.save()

        permanencia = Permanencia.objects.create(
            veiculo_id=veiculo_id,
            vaga=vaga,
            data_hora_entrada=data_hora_entrada or datetime.now(),
            status=Permanencia.Status.ABERTO,
        )

    return Permanencia.objects.select_related("veiculo", "vaga").get(id=permanencia.id)


def registrar_saida(permanencia_id):
    with transaction.atomic():
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

        saida = datetime.now()
        valor = _calcular_valor(permanencia.data_hora_entrada, saida)

        permanencia.data_hora_saida = saida
        permanencia.valor_total = valor
        permanencia.status = Permanencia.Status.FINALIZADO
        permanencia.save()

        vaga = permanencia.vaga
        vaga.status = Vaga.Status.LIVRE
        vaga.save()

    return permanencia


def _calcular_valor(entrada, saida):

    minutos = int((saida - entrada).total_seconds() // 60)
    horas = max(1, math.ceil(minutos / 60))
    return TARIFA_POR_HORA * horas
