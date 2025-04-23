from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserRegistrationForm, UserAdminChangeForm

class CustomUserAdmin(UserAdmin):
    form = UserAdminChangeForm
    add_form = UserRegistrationForm

    list_display = ('username', 'email', 'phone', 'user_type', 'is_staff')  # Изменили 'emails' на 'email'
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),  # Изменили 'emails' на 'email'
        ('Permissions', {'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'user_type', 'password1', 'password2'),  # Изменили 'emails' на 'email'
        }),
    )
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')  # Изменили 'emails' на 'email'
    ordering = ('-date_joined',)

admin.site.register(User, CustomUserAdmin)
