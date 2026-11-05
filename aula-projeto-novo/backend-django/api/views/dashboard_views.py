"""Indicadores do dashboard, equivalentes ao DashboardController do legado."""

from ..models import Permanencia, Vaga
from .comum import erro, responder, tratar_erro_banco


@tratar_erro_banco
def dashboard(request):
    if request.method != "GET":
        return erro("Método não permitido", 405)
    # Os indicadores de vaga contam o campo status, sem cruzar com permanências,
    # como as consultas do legado.
    return responder({
        "totalVagas": Vaga.objects.count(),
        "vagasLivres": Vaga.objects.filter(status=Vaga.Status.LIVRE).count(),
        "vagasOcupadas": Vaga.objects.filter(status=Vaga.Status.OCUPADA).count(),
        "veiculosEstacionados": Permanencia.objects.filter(status=Permanencia.Status.ABERTO).count(),
    })
