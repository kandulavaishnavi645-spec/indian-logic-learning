from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    address_line_1 = forms.CharField(max_length=250, label='Address')
    address_line_2 = forms.CharField(max_length=250, required=False, label='Address (optional)')
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)

