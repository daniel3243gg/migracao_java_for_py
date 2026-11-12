"""Endpoints de vagas, equivalentes ao VagaController do legado."""

from django.db import IntegrityError
from django.db.models import ProtectedError

from ..models import Vaga
from ..serializacao import vaga_to_dict
from .comum import (
    CorpoInvalido,
    converter_id,
    erro,
    ler_json,
    responder,
    texto_preenchido,
    tratar_erro_banco,
)

NAO_ENCONTRADA = "Vaga não encontrada"
NUMERO_DUPLICADO = "Número de vaga já cadastrado"
TIPOS = ("CARRO", "MOTO")
STATUSES = ("LIVRE", "OCUPADA")


def _validar(dados):
    if not texto_preenchido(dados.get("numero")):
        return "Campo 'numero' é obrigatório"
    if dados.get("tipo") not in TIPOS:
        return "Campo 'tipo' deve ser CARRO ou MOTO"
    return None


def _salvar(vaga, dados, pk_atual=None):
    repetida = Vaga.objects.filter(numero=dados["numero"])
    if pk_atual is not None:
        repetida = repetida.exclude(pk=pk_atual)
    if repetida.exists():
        return erro(NUMERO_DUPLICADO, 409)
    vaga.numero = dados["numero"]
    vaga.tipo = dados["tipo"]
    try:
        vaga.save()
    except IntegrityError:
        return erro(NUMERO_DUPLICADO, 409)
    return responder(vaga_to_dict(vaga), 201 if pk_atual is None else 200)


@tratar_erro_banco
def lista_vagas(request):
    if request.method == "GET":
        vagas = Vaga.objects.order_by("numero")
        status = request.GET.get("status")
        if status:
            vagas = vagas.filter(status=status)
        return responder([vaga_to_dict(v) for v in vagas])

    if request.method == "POST":
        try:
            dados = ler_json(request)
        except CorpoInvalido:
            return erro("JSON inválido", 400)
        mensagem = _validar(dados)
        if mensagem:
            return erro(mensagem, 400)
        return _salvar(Vaga(status=Vaga.Status.LIVRE), dados)

    if request.method in ("PUT", "DELETE"):
        return erro("ID obrigatório", 400)
    return erro("Método não permitido", 405)


@tratar_erro_banco
def detalhe_vaga(request, vaga_id):
    if request.method not in ("GET", "PUT", "DELETE"):
        return erro("Método não permitido", 405)
    pk = converter_id(vaga_id)
    if pk is None:
        return erro("ID inválido", 400)

    if request.method == "GET":
        try:
            return responder(vaga_to_dict(Vaga.objects.get(pk=pk)))
        except Vaga.DoesNotExist:
            return erro(NAO_ENCONTRADA, 404)

    if request.method == "PUT":
        try:
            dados = ler_json(request)
        except CorpoInvalido:
            return erro("JSON inválido", 400)
        mensagem = _validar(dados)
        if mensagem:
            return erro(mensagem, 400)
        try:
            vaga = Vaga.objects.get(pk=pk)
        except Vaga.DoesNotExist:
            return erro(NAO_ENCONTRADA, 404)
        status = dados.get("status")
        vaga.status = status if status in STATUSES else Vaga.Status.LIVRE
        return _salvar(vaga, dados, pk_atual=pk)

    try:
        vaga = Vaga.objects.get(pk=pk)
    except Vaga.DoesNotExist:
        return erro(NAO_ENCONTRADA, 404)
    try:
        vaga.delete()
    except ProtectedError:
        return erro("Não é possível excluir vaga com permanências registradas", 409)
    return responder({"message": "Vaga excluída com sucesso"})
