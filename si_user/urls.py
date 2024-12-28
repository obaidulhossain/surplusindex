from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register/', views.register, name="register"),
    path('profile/', views.update_user, name="profile"),
    path('login/', views.user_login, name="my-login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('user-logout', views.user_logout, name="user-logout"),
    path('my-subscription/', views.subscription, name="subscription"),
]
