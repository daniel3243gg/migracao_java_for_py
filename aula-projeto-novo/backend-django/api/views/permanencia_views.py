"""Endpoints de permanências, equivalentes ao PermanenciaController do legado."""

from ..models import Permanencia
from ..serializacao import permanencia_to_dict
from ..services import permanencia_service
from ..services.permanencia_service import NaoEncontrado
from .comum import CorpoInvalido, converter_inteiro, erro, ler_json, responder, tratar_erro_banco

CAMPOS_OBRIGATORIOS = "Campos 'veiculoId' e 'vagaId' são obrigatórios"


@tratar_erro_banco
def lista_permanencias(request):
    if request.method != "GET":
        return erro("Método não permitido", 405)
    permanencias = Permanencia.objects.select_related("veiculo", "vaga").order_by("-data_hora_entrada", "-id")
    status = request.GET.get("status")
    # Filtro vazio é ignorado, como no repositório Java.
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

    # Tarefa 8: veiculoId e vagaId obrigatórios (número inteiro ou texto numérico, como o Gson).
    veiculo_id = converter_inteiro(dados.get("veiculoId"))
    vaga_id = converter_inteiro(dados.get("vagaId"))
    if veiculo_id is None or vaga_id is None:
        return erro(CAMPOS_OBRIGATORIOS, 400)

    try:
        permanencia = permanencia_service.registrar_entrada(veiculo_id, vaga_id)
    except NaoEncontrado as exc:
        return erro(str(exc), 404)
    except ValueError as exc:
        # Veículo já estacionado ou vaga ocupada.
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
        # Permanência já finalizada.
        return erro(str(exc), 409)
    return responder(permanencia_to_dict(permanencia))
