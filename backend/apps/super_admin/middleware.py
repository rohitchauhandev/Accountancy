from django.http import JsonResponse
from django.conf import settings


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "MAINTENANCE_MODE", False):
            if not request.path.startswith("/admin/"):
                return JsonResponse(
                    {"detail": "Service is under maintenance. Please try again later."},
                    status=503,
                )
        return self.get_response(request)
