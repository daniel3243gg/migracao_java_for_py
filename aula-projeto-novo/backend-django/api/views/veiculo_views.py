"""Endpoints de veículos, equivalentes ao VeiculoController do legado."""

from django.db import IntegrityError
from django.db.models import ProtectedError

from ..models import Cliente, Veiculo
from ..serializacao import veiculo_to_dict
from .comum import (
    CorpoInvalido,
    converter_id,
    converter_inteiro,
    erro,
    ler_json,
    responder,
    texto_preenchido,
    tratar_erro_banco,
)

NAO_ENCONTRADO = "Veículo não encontrado"
PLACA_DUPLICADA = "Placa já cadastrada"
CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"
CAMPOS_TEXTO = ("placa", "marca", "modelo", "cor")


def _validar(dados):
    """Mensagem do primeiro campo inválido, na ordem do Java, ou None."""
    for campo in CAMPOS_TEXTO:
        if not texto_preenchido(dados.get(campo)):
            return f"Campo '{campo}' é obrigatório"
    if converter_inteiro(dados.get("clienteId")) is None:
        return "Campo 'clienteId' é obrigatório"
    return None


def _preencher(veiculo, dados):
    for campo in CAMPOS_TEXTO:
        setattr(veiculo, campo, dados[campo])
    veiculo.cliente_id = converter_inteiro(dados["clienteId"])


def _salvar(veiculo, dados, pk_atual=None):
    """Checa duplicidade e cliente, grava e devolve a resposta.

    Placa repetida vem antes de cliente inexistente: no PostgreSQL do legado a
    unicidade estourava antes da FK. O cliente é checado aqui porque a FK do
    SQLite é adiada e só falharia no commit.
    """
    repetida = Veiculo.objects.filter(placa=dados["placa"])
    if pk_atual is not None:
        repetida = repetida.exclude(pk=pk_atual)
    if repetida.exists():
        return erro(PLACA_DUPLICADA, 409)
    if not Cliente.objects.filter(pk=converter_inteiro(dados["clienteId"])).exists():
        return erro(CLIENTE_NAO_ENCONTRADO, 404)
    _preencher(veiculo, dados)
    try:
        veiculo.save()
    except IntegrityError:
        return erro(PLACA_DUPLICADA, 409)
    salvo = Veiculo.objects.select_related("cliente").get(pk=veiculo.pk)
    return responder(veiculo_to_dict(salvo), 201 if pk_atual is None else 200)


@tratar_erro_banco
def lista_veiculos(request):
    if request.method == "GET":
        veiculos = Veiculo.objects.select_related("cliente").order_by("placa")
        return responder([veiculo_to_dict(v) for v in veiculos])

    if request.method == "POST":
        try:
            dados = ler_json(request)
        except CorpoInvalido:
            return erro("JSON inválido", 400)
        mensagem = _validar(dados)
        if mensagem:
            return erro(mensagem, 400)
        return _salvar(Veiculo(), dados)

    if request.method in ("PUT", "DELETE"):
        return erro("ID obrigatório", 400)
    return erro("Método não permitido", 405)


@tratar_erro_banco
def detalhe_veiculo(request, veiculo_id):
    if request.method not in ("GET", "PUT", "DELETE"):
        return erro("Método não permitido", 405)
    pk = converter_id(veiculo_id)
    if pk is None:
        return erro("ID inválido", 400)

    if request.method == "GET":
        try:
            return responder(veiculo_to_dict(Veiculo.objects.select_related("cliente").get(pk=pk)))
        except Veiculo.DoesNotExist:
            return erro(NAO_ENCONTRADO, 404)

    if request.method == "PUT":
        try:
            dados = ler_json(request)
        except CorpoInvalido:
            return erro("JSON inválido", 400)
        mensagem = _validar(dados)
        if mensagem:
            return erro(mensagem, 400)
        try:
            veiculo = Veiculo.objects.get(pk=pk)
        except Veiculo.DoesNotExist:
            return erro(NAO_ENCONTRADO, 404)
        return _salvar(veiculo, dados, pk_atual=pk)

    try:
        veiculo = Veiculo.objects.get(pk=pk)
    except Veiculo.DoesNotExist:
        return erro(NAO_ENCONTRADO, 404)
    try:
        veiculo.delete()
    except ProtectedError:
        return erro("Não é possível excluir veículo com permanências registradas", 409)
    return responder({"message": "Veículo excluído com sucesso"})
