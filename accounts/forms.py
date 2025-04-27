from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator  # Правильный импорт
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


    class Meta:
        model = User
        fields = ['username', 'email',  'password1', 'password2', 'phone', 'last_name',
                  'first_name', 'patronymic',]


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class RoleSelectionForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=User.UserType.choices,
        widget=forms.RadioSelect(),
        label='Выберите вашу роль'
    )

    class Meta:
        model = User
        fields = [
            'role',
            'last_name',
            'first_name',
            'patronymic',
            'phone',
            'passport',
            'avatar'
        ]
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'phone': 'Телефон',
            'passport': 'Паспортные данные',
            'avatar': 'Аватар'
        }
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 999-99-99'}),
            'passport': forms.TextInput(attrs={'placeholder': '1234 567890'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля обязательными
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['phone'].required = True
        self.fields['passport'].required = True


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=18,
        validators=[
            RegexValidator(
                regex=r'^(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$',
                message="Номер должен быть в формате: +7 (XXX) XXX-XX-XX"
            )
        ]
    )

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'phone', 'avatar', 'passport']

        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'avatar': 'Фотография',
            'passport': 'Паспортные данные'
        }