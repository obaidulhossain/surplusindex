from .views import RegistrationView, UsernameValidationView, EmailValidationView, LoginView, VerificationView, user_logout #, LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from .decorators import unauthenticated_user
urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register', unauthenticated_user(RegistrationView.as_view()), name="register"),
    path('login', unauthenticated_user(LoginView.as_view()), name="login"),
    path('user-logout', views.user_logout, name="user-logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validation-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate_email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate")
]