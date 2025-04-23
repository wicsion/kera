from django.shortcuts import  get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import BrokerProfile, BrokerReview
from properties.forms import PropertyForm
from properties.models import PropertyType
from accounts.models import Subscription  # Импорт модели подписок
from properties.models import Property
from .forms import BrokerProfileForm, BrokerReviewForm
from django.utils import timezone

class BrokerPropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'brokers/property_list.html'
    context_object_name = 'properties'

    def get_queryset(self):
        return Property.objects.filter(broker=self.request.user)


class PropertyCreateWithSubscriptionCheck(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def form_valid(self, form):
        if self.request.user.user_type == 'broker':
            active_sub = Subscription.objects.filter(
                user=self.request.user,
                end_date__gte=timezone.now().date()
            ).exists()

            if not active_sub and form.cleaned_data.get('is_premium'):
                return HttpResponseForbidden("Требуется активная подписка для премиум-объявлений")

        form.instance.user = self.request.user
        return super().form_valid(form)

class BrokerListView(ListView):
    model = BrokerProfile
    template_name = 'brokers/broker_list.html'
    context_object_name = 'brokers'
    paginate_by = 10

    def get_queryset(self):
        return BrokerProfile.objects.filter(is_archived=False, is_approved=True)

class BrokerDetailView(DetailView):
    model = BrokerProfile
    template_name = 'brokers/broker_detail.html'
    context_object_name = 'broker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.filter(
            broker=self.object.user,
            status='active',
            is_approved=True
        )[:4]
        context['reviews'] = BrokerReview.objects.filter(
            broker=self.object,
            is_approved=True
        )[:5]
        return context


class BrokerProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BrokerProfile
    form_class = BrokerProfileForm
    template_name = 'brokers/broker_update.html'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse_lazy('broker-detail', kwargs={'pk': self.object.pk})


class BrokerReviewCreateView(LoginRequiredMixin, CreateView):
    model = BrokerReview
    form_class = BrokerReviewForm
    template_name = 'brokers/review_create.html'

    def form_valid(self, form):
        form.instance.broker = get_object_or_404(BrokerProfile, pk=self.kwargs['pk'])
        form.instance.client = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('broker-detail', kwargs={'pk': self.kwargs['pk']})