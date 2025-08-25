from django.urls import path
from . import views

urlpatterns = [
    path('save-sidebar-setting/', views.save_sidebar_setting, name='save_sidebar_setting'),
]