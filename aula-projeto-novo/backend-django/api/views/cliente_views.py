from django.http import JsonResponse


def lista_clientes(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)


def detalhe_cliente(request, cliente_id):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)
