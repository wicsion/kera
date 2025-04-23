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


class RoleSelectionForm(forms.Form):
    role = forms.ChoiceField(
        choices=User.UserType.choices[0:3],
        widget=forms.RadioSelect(),
        label='Выберите вашу роль'
    )


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=18,
        validators=[
            RegexValidator(
                regex=r'^\+7\s?\(?\d{3}\)?\s?\d{3}-\d{2}-\d{2}$',
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