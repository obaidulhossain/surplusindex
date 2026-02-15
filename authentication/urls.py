from .views import *
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from django.contrib.auth import views as auth_views
from .decorators import unauthenticated_user
urlpatterns = [
    path('', views.homepage, name="homepage"),
    
    # path('login', unauthenticated_user(LoginView.as_view()), name="login"),
    path('login', views.Login, name="login"),
    path('LoginAuthenticate',views.LoginAuthenticate, name="LoginAuthenticate"),

    path('register', views.Register, name="register"),
    path("register/start/", views.start_registration, name="start_registration"),
    path("register/complete/", views.complete_registration, name="complete_registration"),
    path('validate-username', views.ValidateUsername, name="validation-username"),
    path('validate-email', views.ValidateEmail, name="validate_email"),
    # path('register', unauthenticated_user(RegistrationView.as_view()), name="register"),
    # path('start-registration/',views.start_registration, name="start_registration"),
    # path('complete-registration/',views.complete_registration, name="complete_registration"),

    
    path('user-logout', views.user_logout, name="user-logout"),
    # path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validation-username"),
    # path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate_email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
    path('password-change/', PasswordChangeView.as_view(template_name='registration/password_change_form.html', success_url='/password-change/done/'), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    #reset password
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="authentication/password_reset.html", email_template_name="authentication/password_reset_email.txt", html_email_template_name="authentication/password_reset_email.html", subject_template_name="authentication/password_reset_subject.txt",), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="authentication/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/",auth_views.PasswordResetCompleteView.as_view(template_name="authentication/password_reset_complete.html"), name="password_reset_complete"),
]