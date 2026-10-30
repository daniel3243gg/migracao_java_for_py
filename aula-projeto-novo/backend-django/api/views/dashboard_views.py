from django.http import JsonResponse


def dashboard(request):
    return JsonResponse({"detail": "Endpoint em implementação."}, status=501)
