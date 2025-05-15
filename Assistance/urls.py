from django.urls import path
from . import views

urlpatterns = [
    path('support', views.getAssistance, name="get_assistance"),
]