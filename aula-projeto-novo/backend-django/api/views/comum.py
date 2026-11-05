"""Utilitários HTTP compartilhados pelas views da API.

Reproduzem o contrato do backend Java legado (HttpUtil e JsonUtil):
erros como {"error": "..."}, JSON em UTF-8 e 500 para falha de banco.
"""

import json
from functools import wraps

from django.db import DatabaseError
from django.http import JsonResponse


class CorpoInvalido(Exception):
    """Corpo da requisição não é um objeto JSON válido."""


def responder(dados, status=200):
    # ensure_ascii=False e charset explícito: igual ao Gson, que devolvia UTF-8 sem escapes.
    return JsonResponse(
        dados,
        status=status,
        safe=False,
        json_dumps_params={"ensure_ascii": False},
        content_type="application/json; charset=UTF-8",
    )


def erro(mensagem, status):
    return responder({"error": mensagem}, status)


def ler_json(request):
    """Lê o corpo como objeto JSON; levanta CorpoInvalido se não for um dict."""
    try:
        dados = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise CorpoInvalido()
    if not isinstance(dados, dict):
        raise CorpoInvalido()
    return dados


def converter_id(texto):
    """ID do caminho como int, ou None se não for número inteiro (Long.parseLong no Java)."""
    try:
        return int(texto)
    except (TypeError, ValueError):
        return None


def texto_preenchido(valor):
    """Equivalente a valor != null && !valor.trim().isEmpty() do Java."""
    return isinstance(valor, str) and valor.strip() != ""


def converter_inteiro(valor):
    """Inteiro vindo do JSON: número inteiro ou texto só com dígitos (o Gson aceitava ambos)."""
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, str) and valor.isascii() and valor.isdigit():
        return int(valor)
    return None


def tratar_erro_banco(view):
    """Falha de banco não prevista vira 500, como o catch (SQLException) dos controllers."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except DatabaseError as exc:
            return erro(f"Erro no banco de dados: {exc}", 500)

    return envolvida
