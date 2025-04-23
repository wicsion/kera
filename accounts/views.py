from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, FormView, UpdateView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import random
import string

from .models import User, Subscription, UserActivity
from .forms import UserRegistrationForm, RoleSelectionForm, ProfileForm


def home_view(request):

    return render(request, 'home.html')


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('email_verification_sent')

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_active = False  # Деактивируем до верификации
            user.verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            user.save()
            self.send_verification_email(user)
            return redirect(self.success_url)  # Явный редирект
        except Exception as e:
            form.add_error(None, f"Ошибка: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def send_verification_email(self, user):
        verification_link = self.request.build_absolute_uri(
            f"/accounts/verify-email/{user.verification_token}/"
        )
        subject = 'Подтверждение email'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        text_content = f'Для подтверждения email перейдите по ссылке: {verification_link}'
        html_content = render_to_string('emails/verify_email.html', {
            'verification_link': verification_link,
            'user': user
        })
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class CompleteRegistrationView(LoginRequiredMixin, View):
    template_name = 'accounts/complete-registration.html'

    def get(self, request):
        # Инициализация обеих форм при GET-запросе
        role_form = RoleSelectionForm()
        profile_form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })

    def post(self, request):
        role_form = RoleSelectionForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if role_form.is_valid() and profile_form.is_valid():
            user = profile_form.save(commit=False)
            user.user_type = role_form.cleaned_data['role']
            user.save()
            return redirect('dashboard')

        # При ошибках снова показываем формы с данными
        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })


def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True  # Убедитесь, что это поле используется
        user.is_active = True    # Активируем пользователя
        user.verification_token = None
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('complete_registration')
    except User.DoesNotExist:
        return redirect('invalid_token')


# Остальные представления остаются без изменений
class EmailVerificationSentView(TemplateView):
    template_name = 'accounts/email_verification_sent.html'


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            UserActivity.objects.create(user=user, action="Вход в систему")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        UserActivity.objects.create(user=request.user, action="Выход из системы")
    logout(request)
    return redirect('home')


class BrokerProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    fields = ['avatar']
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user


class SubscriptionView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'accounts/subscriptions.html'

    def get_queryset(self):
        return self.request.user.subscriptions.filter(is_active=True)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    user = request.user

    if user.user_type == User.UserType.BROKER:
        context.update({
            'properties': user.broker_properties.all()[:5],
            'subscriptions': user.subscriptions.filter(is_active=True),
            'activities': UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]
        })
    elif user.user_type == User.UserType.DEVELOPER:
        context['developer_properties'] = user.developer_properties.all()[:5]
    elif user.user_type == User.UserType.CLIENT:
        context['favorite_properties'] = user.favorites.all()[:5]

    return render(request, 'accounts/dashboard.html', context)


def invalid_token_view(request):
    return render(request, 'accounts/invalid_token.html')