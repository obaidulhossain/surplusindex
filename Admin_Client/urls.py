from django.urls import path
from . import views



urlpatterns = [
    path('all_clients/', views.allClients, name="all_clients"),
    path('client_detail/', views.clientDetail, name="client_detail"),
    path('updateDeliveryStatus/', views.updateDeliveryStatus, name="updateDeliveryStatus"),
    path('updateOrderStatus/', views.updateOrderStatus, name="updateOrderStatus"),
    

]