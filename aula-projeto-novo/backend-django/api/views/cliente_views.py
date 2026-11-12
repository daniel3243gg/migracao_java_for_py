"""Endpoints de clientes, equivalentes ao ClienteController do legado."""

from django.db import IntegrityError
from django.db.models import ProtectedError

from ..models import Cliente
from ..serializacao import cliente_to_dict
from .comum import (
    CorpoInvalido,
    converter_id,
    erro,
    ler_json,
    responder,
    texto_preenchido,
    tratar_erro_banco,
)

NAO_ENCONTRADO = "Cliente não encontrado"
CPF_DUPLICADO = "CPF já cadastrado"


def _opcional(valor):
    if valor is None or isinstance(valor, str):
        return valor
    return str(valor)


def _validar(dados):
    """Mensagem de erro do primeiro campo inválido, na ordem do Java, ou None."""
    if not texto_preenchido(dados.get("nome")):
        return "Campo 'nome' é obrigatório"
    if not texto_preenchido(dados.get("cpf")):
        return "Campo 'cpf' é obrigatório"
    return None


def _preencher(cliente, dados):
    cliente.nome = dados["nome"]
    cliente.cpf = dados["cpf"]
    cliente.telefone = _opcional(dados.get("telefone"))
    cliente.email = _opcional(dados.get("email"))


@tratar_erro_banco
def lista_clientes(request):
    if request.method == "GET":
        return responder([cliente_to_dict(c) for c in Cliente.objects.order_by("nome")])

    if request.method == "POST":
        try:
            dados = ler_json(request)
        except CorpoInvalido:
            return erro("JSON inválido", 400)
        mensagem = _validar(dados)
        if mensagem:
            return erro(mensagem, 400)
        if Cliente.objects.filter(cpf=dados["cpf"]).exists():
            return erro(CPF_DUPLICADO, 409)
        cliente = Cliente()
        _preencher(cliente, dados)
        try:
            cliente.save()
        except IntegrityError:
            return erro(CPF_DUPLICADO, 409)
        return responder(cliente_to_dict(cliente), 201)

    if request.method in ("PUT", "DELETE"):
        return erro("ID obrigatório", 400)
    return erro("Método não permitido", 405)


@tratar_erro_banco
def detalhe_cliente(request, cliente_id):
    if request.method not in ("GET", "PUT", "DELETE"):
        return erro("Método não permitido", 405)
    pk = converter_id(cliente_id)
    if pk is None:
        return erro("ID inválido", 400)

    if request.method == "GET":
        try:
            return responder(cliente_to_dict(Cliente.objects.get(pk=pk)))
        except Cliente.DoesNotExist:
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
            cliente = Cliente.objects.get(pk=pk)
        except Cliente.DoesNotExist:
            return erro(NAO_ENCONTRADO, 404)
        if Cliente.objects.filter(cpf=dados["cpf"]).exclude(pk=pk).exists():
            return erro(CPF_DUPLICADO, 409)
        _preencher(cliente, dados)
        try:
            cliente.save()
        except IntegrityError:
            return erro(CPF_DUPLICADO, 409)
        return responder(cliente_to_dict(cliente))

    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return erro(NAO_ENCONTRADO, 404)
    try:
        cliente.delete()
    except ProtectedError:
        return erro("Não é possível excluir cliente com veículos cadastrados", 409)
    return responder({"message": "Cliente excluído com sucesso"})
