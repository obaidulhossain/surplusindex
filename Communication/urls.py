from django.urls import path
from . import views

urlpatterns = [

#--------------url for settings page--------------------
    #path('communication/',views.Communication, name='communication'),
    path("send/", views.send_mail_view, name="send_mail"),
]