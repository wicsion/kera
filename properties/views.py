from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django_filters.views import FilterView
from .models import Property, PropertyImage, Favorite
from .filters import PropertyFilter
from .forms import PropertyForm, PropertyImageForm


class PropertyListView(FilterView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    filterset_class = PropertyFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            is_approved=True,
            status='active'
        ).select_related('property_type', 'broker', 'developer')


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                property=self.object
            ).exists()
        return context


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'active'
        if self.request.user.user_type == 'broker':
            form.instance.broker = self.request.user
        elif self.request.user.user_type == 'developer':
            form.instance.developer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('property-detail', kwargs={'pk': self.object.pk})


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse_lazy('property-detail', kwargs={'pk': self.object.pk})


def toggle_favorite(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    property = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property
    )

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'is_favorite': False})
    return JsonResponse({'status': 'added', 'is_favorite': True})

class BrokerFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        property = get_object_or_404(Property, pk=pk)
        Favorite.objects.get_or_create(
            user=request.user,
            property=property,
            is_broker_favorite=True
        )
        return JsonResponse({'status': 'added'})