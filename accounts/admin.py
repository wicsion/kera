from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Property, Favorite, ContactRequest  # Импорт новых моделей
from .forms import UserRegistrationForm, UserAdminChangeForm

class CustomUserAdmin(UserAdmin):
    form = UserAdminChangeForm
    add_form = UserRegistrationForm

    list_display = ('username', 'email', 'phone', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Permissions', {'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'user_type', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'price', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'creator__user_type')
    actions = ['approve_properties', 'reject_properties']
    search_fields = ('title', 'creator__username')
    raw_id_fields = ('creator',)

    def approve_properties(self, request, queryset):
        queryset.update(is_approved=True)
    approve_properties.short_description = "Одобрить выбранные объекты"

    def reject_properties(self, request, queryset):
        queryset.update(is_approved=False)
    reject_properties.short_description = "Отклонить выбранные объекты"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'broker', 'created_at')
    list_filter = ('user__user_type',)
    raw_id_fields = ('user', 'property', 'broker')

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'broker', 'property', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'broker__user_type')
    raw_id_fields = ('requester', 'broker', 'property')

admin.site.register(User, CustomUserAdmin)

