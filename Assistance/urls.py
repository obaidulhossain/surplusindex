from django.urls import path
from . import views

urlpatterns = [
    path('support', views.getAssistance, name="get_assistance"),
    path('support/<int:conv_id>/', views.fetch_messages, name='fetch_messages'),
    path("support/send/", views.send_message, name="send_message"),

    path("conversation", views.ConversationView, name="conversation"),
    path('conversation/<int:conv_id>/', views.fetch_messages_admin, name='fetch_messages_admin'),
    path("conversation/send/", views.send_message_admin, name="send_message_admin"),
    path("manage_conversation", views.ManageConversation, name="manage_conversation"),
]