from django.urls import path, include
from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name="login"),
    path('signup/', views.UserRegistrationView.as_view(), name="register"),
    path('settings/', views.SettingsView.as_view(), name="settings"),
    path('settings/new-password/', views.ChangePasswordView.as_view(), name="new-password"),
    path('logout/', views.logout_view, name="logout"),
]
