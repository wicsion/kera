from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('Phone Number'), max_length=18, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=150, blank=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True, verbose_name='Токен верификации')

    class UserType(models.TextChoices):
        CLIENT = 'client', _('Client')
        BROKER = 'broker', _('Broker')
        DEVELOPER = 'developer', _('Developer')

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name=_('User Type')
    )

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    passport = models.CharField(_('Passport Data'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    @property
    def is_broker(self):
        return self.user_type == self.UserType.BROKER

    @property
    def is_developer(self):
        return self.user_type == self.UserType.DEVELOPER

    @property
    def is_profile_complete(self):
        return all([
            self.user_type,
            self.last_name and self.last_name.strip() != '',
            self.first_name and self.first_name.strip() != '',
            self.phone and self.phone.strip() != '',
            self.passport and self.passport.strip() != ''
        ])

class UserActivity(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    developer = models.ForeignKey(
        'developers.DeveloperProfile',
        on_delete=models.CASCADE
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'developer')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user} → {self.developer}"



class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_properties')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_properties', blank=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    broker = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='favorited_brokers')
    created_at = models.DateTimeField(auto_now_add=True)

class ContactRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)