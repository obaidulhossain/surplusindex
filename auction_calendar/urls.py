from django.urls import path
from . import views

urlpatterns = [
    path('auction_calendar/', views.auction_calendar, name='auction_calendar'),
    path('',views.client_access, name='client_access'),
    path('dashboard/',views.dashboard, name='dashboard'),
]


