from django.http import JsonResponse


def lista_veiculos(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)


def detalhe_veiculo(request, veiculo_id):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)
