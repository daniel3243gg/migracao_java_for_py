from django.http import JsonResponse


def lista_vagas(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)


def detalhe_vaga(request, vaga_id):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)
