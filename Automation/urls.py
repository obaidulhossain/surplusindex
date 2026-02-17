from django.urls import path
from . import views


urlpatterns = [
    path('', views.Automate, name="automate"),
    path("direct-subscribe/", views.direct_subscribe, name="direct-subscribe"),
]