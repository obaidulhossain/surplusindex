from django.urls import path
from . import views




urlpatterns = [
    path('', views.index, name="propertydata" ),
    path('add/', views.addproperty, name="addproperty" ),
]