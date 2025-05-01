from django.urls import path
from .views import (
    RegisterView,
    verify_email,
    EmailVerificationSentView,
    BrokerProfileUpdateView,
    SubscriptionView,
    dashboard_view,
    invalid_token_view,
    login_view,
    logout_view,
    CompleteRegistrationView,
    PropertyCreateView,
    ToggleFavoriteView,
    ContactRequestView,
    ContactRequestDetailView,
    MessageCreateView,

)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/update/', BrokerProfileUpdateView.as_view(), name='profile-update'),
    path('subscriptions/', SubscriptionView.as_view(), name='subscriptions'),
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
    path('invalid-token/', invalid_token_view, name='invalid_token'),
    path('email-verification-sent/', EmailVerificationSentView.as_view(), name='email_verification_sent'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete_registration'),
    path('property/create/', PropertyCreateView.as_view(), name='create_property'),
    path('toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('broker/<int:pk>/contact/', ContactRequestView.as_view(), name='contact_broker'),
    path('contact-request/new/', ContactRequestView.as_view(), name='new_contact_request'),
    path('contact-request/<int:pk>/', ContactRequestDetailView.as_view(), name='contact_request_detail'),
    path('contact-request/<int:pk>/message/', MessageCreateView.as_view(), name='add_message'),

]

