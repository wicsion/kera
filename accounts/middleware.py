from django.shortcuts import redirect
from .models import UserActivity

class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Логирование активности
        response = self.get_response(request)
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                action=f"Посещение страницы: {request.path}"
            )
        return response

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_paths = [
            '/accounts/complete-registration/',
            '/accounts/logout/',
            '/static/',
            '/media/',
            '/accounts/verify-email/',
            '/accounts/invalid-token/',
            '/accounts/login/'
        ]

        if request.path in excluded_paths:
            return self.get_response(request)

        if request.user.is_authenticated:
            pass


        return self.get_response(request)