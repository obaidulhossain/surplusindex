from django.urls import path
from . import views

urlpatterns = [
    
    path('leads/', views.availableLeads, name="leads"),
    path('purchaseLeads', views.purchaseLeads, name="purchaseLeads"),
    path('hide-leads', views.hidefromallLeads, name="hide-leads"),

    path('archive_leads', views.archivefromMyLeads, name="archive_leads"),
    


    path('myleads/', views.myLeads, name="myleads"),
    path('leads-detail/', views.leadsDetail, name="leads-detail"),
    path('update_status', views.updateStatus, name="update_status"),
    path('updateStatus_ajax/', views.updateStatus_ajax, name="updateStatus_ajax"),
    path('updateArchived/', views.updateArchived, name="updateArchived"),

    path('export_filtered_data', views.export_data, name="export_filtered_data"),
    path('export_mylead', views.exportMyleads, name="export_mylead"),
    
    

]