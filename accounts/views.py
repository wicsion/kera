from django.views.generic import DetailView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import  UpdateView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.views.generic import CreateView
import random
import string

from .models import User, UserActivity, Subscription , Property, Favorite, ContactRequest, Message
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
            user.is_active = False
            user.verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            user.save()
            self.send_verification_email(user)
            return redirect(self.success_url)
        except Exception as e:
            form.add_error(None, f"Ошибка: {str(e)}")
            return self.form_invalid(form)

    def send_verification_email(self, user):
        verification_link = self.request.build_absolute_uri(
            f"/accounts/verify-email/{user.verification_token}/"
        )
        subject = 'Подтверждение email'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        html_content = render_to_string('emails/verify_email.html', {
            'verification_link': verification_link,
            'user': user
        })
        msg = EmailMultiAlternatives(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()


class CompleteRegistrationView(LoginRequiredMixin, View):
    template_name = 'accounts/complete-registration.html'

    def get(self, request):
        role_form = RoleSelectionForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })

    def post(self, request):
        # Логирование входящих данных
        role_form = RoleSelectionForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if role_form.is_valid() and profile_form.is_valid():
            user = role_form.save(commit=False)
            user.user_type = role_form.cleaned_data['role']
            profile_form.save()  # Сохраняем связанные данные профиля

            # Обновляем статусы
            user.is_verified = True
            user.is_active = True
            user.save()

            profile_data = profile_form.cleaned_data
            for field in ['last_name', 'first_name', 'patronymic', 'phone', 'passport', 'avatar']:
                setattr(user, field, profile_data.get(field))
            user.save()
            return redirect('dashboard')

        else:

            import logging
            logger = logging.getLogger('django')
            logger.error("Role form errors: %s", role_form.errors.as_json())
            logger.error("Profile form errors: %s", profile_form.errors.as_json())

        return render(request, self.template_name, {
            'role_form': role_form,
            'profile_form': profile_form
        })


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

    active_tab = request.GET.get('tab', 'properties')
    user = request.user
    context = {'active_tab': active_tab}

    # Общие данные
    context.update({
        'activities': UserActivity.objects.filter(user=user).order_by('-timestamp')[:10],
        'contact_requests': user.received_requests.all() if user.is_broker else []
    })

    # Данные по ролям
    if user.user_type == User.UserType.BROKER:
        context.update({
            'my_properties': user.created_properties.all(),
            'subscriptions': user.subscriptions.filter(is_active=True)
        })
    elif user.user_type == User.UserType.DEVELOPER:
        context['developer_properties'] = user.created_properties.filter(is_approved=True)
    elif user.user_type == User.UserType.CLIENT:
        # Фильтрация данных для клиента
        if active_tab == 'properties':
            context['favorite_properties'] = user.account_favorites.filter(property__isnull=False)
        else:
            context['broker_favorites'] = user.broker_favorites.all()

    return render(request, 'accounts/dashboard.html', context)


def invalid_token_view(request):
    return render(request, 'accounts/invalid_token.html')


class RoleSelectionView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/role_selection.html'
    form_class = RoleSelectionForm
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_verified = True
        user.save()
        return super().form_valid(form)


def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_active = True
        user.verification_token = ''
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('complete_registration')
    except User.DoesNotExist:
        return redirect('invalid_token')


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    fields = ['title', 'description', 'price']
    template_name = 'accounts/property_create.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request):
        obj_type = request.POST.get('type')
        obj_id = request.POST.get('id')

        if obj_type == 'property':
            obj = get_object_or_404(Property, id=obj_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                property=obj
            )
            if not created:
                favorite.delete()

        elif obj_type == 'broker':
            broker = get_object_or_404(User, id=obj_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                broker=broker
            )
            if not created:
                favorite.delete()

        return JsonResponse({'status': 'ok'})


class ContactRequestView(LoginRequiredMixin, CreateView):
    model = ContactRequest
    fields = ['broker', 'property']
    template_name = 'accounts/contact_request_form.html'

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contact_request_detail', kwargs={'pk': self.object.pk})


class ContactRequestDetailView(LoginRequiredMixin, DetailView):
    model = ContactRequest
    template_name = 'accounts/contact_request_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all()
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['text']

    def form_valid(self, form):
        contact_request = get_object_or_404(ContactRequest, pk=self.kwargs['pk'])
        form.instance.contact_request = contact_request
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contact_request_detail', kwargs={'pk': self.kwargs['pk']})