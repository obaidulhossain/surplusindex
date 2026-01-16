from django.urls import path
from . import views


urlpatterns = [

# Urls for Upload Data Section
path('', views.Automation, name="automation"),
]