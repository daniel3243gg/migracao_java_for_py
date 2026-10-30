from django.http import JsonResponse


def entrada(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)


def saida(request, permanencia_id):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)


def lista_permanencias(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)
