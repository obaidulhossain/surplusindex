from django.urls import path
from . import views




urlpatterns = [
    path('', views.index, name="propertydata" ),
    path('add/', views.addProperty, name="addproperty"),
    path('leads/', views.allLeads, name="leads"),
    path('buy-leads', views.addtoMyList, name="buy-leads"),
    path('hide-leads', views.hidefromallLeads, name="hide-leads")
]