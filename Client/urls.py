from django.urls import path
from . import views

urlpatterns = [
    path('available_leads/', views.availableLeads, name="available_leads"),
    path('purchaseLeads', views.purchaseLeads, name="purchaseLeads"),
    path('hide-leads', views.hidefromallLeads, name="hide-leads"),
    path('export_filtered_data', views.export_data, name="export_filtered_data"),

]