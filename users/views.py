from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .models import UserModel
from .forms import UserLoginForm, UserRegistrationForm


class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = UserLoginForm
    model = UserModel
    success_url = "/"

    def get_success_url(self):
        return self.success_url or '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UserRegistrationView(CreateView):
    template_name = 'registration.html'
    form_class = UserRegistrationForm
    model = UserModel
    success_url = "/login/"


class ChangePasswordView(PasswordChangeView):
    template_name = 'new_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account:settings')


class SettingsView(TemplateView):
    template_name = 'settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


def logout_view(request):
    logout(request)
    return redirect('index')
