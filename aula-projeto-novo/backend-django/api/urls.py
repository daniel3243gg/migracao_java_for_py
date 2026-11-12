from django.urls import path

from .views import dashboard_views, cliente_views, permanencia_views, vaga_views, veiculo_views


def rota(padrao, view):
    """Registra a rota com e sem barra final.

    O frontend legado chama /api/... sem barra e o roteiro lista as URLs com
    barra. APPEND_SLASH está desligado porque o redirecionamento perderia o
    corpo de POST e PUT, então as duas formas são registradas aqui.
    """
    return [path(padrao, view), path(padrao + "/", view)]


urlpatterns = [
    *rota("clientes", cliente_views.lista_clientes),
    *rota("clientes/<str:cliente_id>", cliente_views.detalhe_cliente),
    *rota("veiculos", veiculo_views.lista_veiculos),
    *rota("veiculos/<str:veiculo_id>", veiculo_views.detalhe_veiculo),
    *rota("vagas", vaga_views.lista_vagas),
    *rota("vagas/<str:vaga_id>", vaga_views.detalhe_vaga),
    *rota("permanencias", permanencia_views.lista_permanencias),
    *rota("permanencias/entrada", permanencia_views.entrada),
    *rota("permanencias/<int:permanencia_id>/saida", permanencia_views.saida),
    *rota("dashboard", dashboard_views.dashboard),
]
