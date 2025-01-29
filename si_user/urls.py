from django.urls import path
from . import views

urlpatterns = [
#    path('register/', views.register, name="register"),
    path('profile/', views.update_user, name="profile"),
#    path('login/', views.user_login, name="my-login"),
#    path('dashboard/', views.dashboard, name="dashboard"),
    path('my-subscription/', views.subscription, name="subscription"),
        
]
