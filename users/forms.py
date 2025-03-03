from django import forms

from notes.models import Note
from .models import UserModel
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'password',)


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2')
