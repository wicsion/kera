from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями"""
    # Оставляем только email как обязательное
    email = models.EmailField(_('email address'), unique=True)

    # Делаем остальные поля необязательными
    phone = models.CharField(_('Phone Number'), max_length=18, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=150, blank=True)

    verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Токен верификации'
    )


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



    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Avatar')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified')
    )
    passport = models.CharField(
        _('Passport Data'),
        max_length=100,
        blank=True
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    @property
    def is_broker(self):
        return self.user_type == self.UserType.BROKER

    @property
    def is_developer(self):
        return self.user_type == self.UserType.DEVELOPER

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