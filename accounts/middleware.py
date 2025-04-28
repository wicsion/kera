from django.shortcuts import redirect
from .models import UserActivity

class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        def __call__(self, request):
            if request.user.is_authenticated:
                print(f"Профиль завершен: {request.user.is_profile_complete}")
                print(f"Данные пользователя: {request.user.__dict__}")

        excluded_paths = [
            '/accounts/logout/',
            '/static/',
            '/media/',
            '/accounts/verify-email/',
            '/accounts/invalid-token/',
            '/accounts/login/',
            '/accounts/select-role/',
            '/accounts/dashboard/',
            '/accounts/complete-registration/'  # Добавлено исключение
        ]

        if request.user.is_authenticated:
            if not request.user.is_profile_complete:
                if request.path not in excluded_paths:
                    return redirect('complete_registration')

        return self.get_response(request)