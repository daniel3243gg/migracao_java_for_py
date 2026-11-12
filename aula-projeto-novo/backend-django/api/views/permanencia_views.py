"""Endpoints de permanências, equivalentes ao PermanenciaController do legado."""

from datetime import datetime
from zoneinfo import ZoneInfo

from ..models import Permanencia
from ..serializacao import permanencia_to_dict
from ..services import permanencia_service
from ..services.permanencia_service import NaoEncontrado
from .comum import CorpoInvalido, converter_inteiro, erro, ler_json, responder, tratar_erro_banco

CAMPOS_OBRIGATORIOS = "Campos 'veiculoId' e 'vagaId' são obrigatórios"


def _data_hora_entrada(dados):
    """Lê dataHoraEntrada opcional no formato ISO 8601.

    O banco usa datetimes sem fuso (USE_TZ=False). Valores com fuso são
    convertidos para o horário de São Paulo antes de serem persistidos.
    """
    valor = dados.get("dataHoraEntrada")
    if valor is None:
        return None
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError("Campo 'dataHoraEntrada' inválido")
    try:
        texto = valor.strip()
        if texto.endswith("Z"):
            texto = texto[:-1] + "+00:00"
        entrada = datetime.fromisoformat(texto)
    except ValueError as exc:
        raise ValueError("Campo 'dataHoraEntrada' inválido") from exc
    if entrada.tzinfo is not None:
        entrada = entrada.astimezone(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
    return entrada


@tratar_erro_banco
def lista_permanencias(request):
    if request.method != "GET":
        return erro("Método não permitido", 405)
    permanencias = Permanencia.objects.select_related("veiculo", "vaga").order_by("-data_hora_entrada", "-id")
    status = request.GET.get("status")
    if status:
        permanencias = permanencias.filter(status=status)
    return responder([permanencia_to_dict(p) for p in permanencias])


@tratar_erro_banco
def entrada(request):
    if request.method != "POST":
        return erro("Método não permitido", 405)
    try:
        dados = ler_json(request)
    except CorpoInvalido:
        return erro("JSON inválido", 400)

    veiculo_id = converter_inteiro(dados.get("veiculoId"))
    vaga_id = converter_inteiro(dados.get("vagaId"))
    if veiculo_id is None or vaga_id is None:
        return erro(CAMPOS_OBRIGATORIOS, 400)
    try:
        data_hora_entrada = _data_hora_entrada(dados)
    except ValueError as exc:
        return erro(str(exc), 400)

    try:
        permanencia = permanencia_service.registrar_entrada(
            veiculo_id, vaga_id, data_hora_entrada=data_hora_entrada
        )
    except NaoEncontrado as exc:
        return erro(str(exc), 404)
    except ValueError as exc:
        return erro(str(exc), 409)
    return responder(permanencia_to_dict(permanencia), 201)


@tratar_erro_banco
def saida(request, permanencia_id):
    if request.method != "PUT":
        return erro("Método não permitido", 405)
    try:
        permanencia = permanencia_service.registrar_saida(permanencia_id)
    except NaoEncontrado as exc:
        return erro(str(exc), 404)
    except ValueError as exc:
        return erro(str(exc), 409)
    return responder(permanencia_to_dict(permanencia))
