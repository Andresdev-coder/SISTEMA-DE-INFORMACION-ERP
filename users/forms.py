from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import User

class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        label= 'Username',
        widget= forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20',
            'placeholder': 'Ingresa tu usuario'
        })
    )
    
    password = forms.CharField(
            label= 'Password',
            widget= forms.PasswordInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20',
                'placeholder': 'Ingresa tu contraseña'
            })
    )
    
    class Meta:
        
        model = User
        fields = ['username', 'password']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo electrónico'}
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}))
    new_password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}))
    new_password2 = forms.CharField(label='Confirmar nueva contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}))
