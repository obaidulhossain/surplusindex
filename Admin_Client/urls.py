from django.urls import path
from . import views



urlpatterns = [
    path('all_clients/', views.allClients, name="all_clients"),
    path('update_credits/', views.updateCredits, name="update_credits"),
    
    path('client_detail/', views.clientDetail, name="client_detail"),
    path('client_settings/', views.clientSettings, name="client_settings"),
    path('create_client/', views.registerClient, name="create_client"),
    path('updateDeliveryStatus/', views.updateDeliveryStatus, name="updateDeliveryStatus"),
    path('updateOrderStatus/', views.updateOrderStatus, name="updateOrderStatus"),
    path('UpdatePaymentStatus', views.UpdatePaymentStatus, name="UpdatePaymentStatus"),
    path('CreateOrder', views.CreateOrder, name="CreateOrder"),
    path('createDelivery', views.createDelivery, name="createDelivery"),
    
    path('resend-activation/', views.resend_activation_email, name='resend_activation_email'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),


]