from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('auction_calendar/', views.auction_calendar, name='auction_calendar'),
]


