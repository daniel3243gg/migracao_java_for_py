from django.urls import path

from .views import dashboard_views, cliente_views, permanencia_views, vaga_views, veiculo_views

urlpatterns = [
    path("clientes", cliente_views.lista_clientes),
    path("clientes/<int:cliente_id>", cliente_views.detalhe_cliente),
    path("veiculos", veiculo_views.lista_veiculos),
    path("veiculos/<int:veiculo_id>", veiculo_views.detalhe_veiculo),
    path("vagas", vaga_views.lista_vagas),
    path("vagas/<int:vaga_id>", vaga_views.detalhe_vaga),
    path("permanencias", permanencia_views.lista_permanencias),
    path("permanencias/entrada", permanencia_views.entrada),
    path("permanencias/<int:permanencia_id>/saida", permanencia_views.saida),
    path("dashboard", dashboard_views.dashboard),
]
