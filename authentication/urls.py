from .views import RegistrationView, UsernameValidationView, EmailValidationView, LoginView, user_logout #, LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('user-logout', views.user_logout, name="user-logout"),
    #path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validation-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate_email")
]