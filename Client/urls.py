from django.urls import path
from . import views

urlpatterns = [
    
    path('leads/', views.availableLeads, name="leads"),
    path('purchaseLeads', views.purchaseLeads, name="purchaseLeads"),
    path('auto_download_purchased_leads', views.auto_download_purchased_leads, name="auto_download_purchased_leads"),
    path('hide-leads', views.hidefromallLeads, name="hide-leads"),

    path('archive_leads', views.archivefromMyLeads, name="archive_leads"),
    


    path('myleads/', views.myLeads, name="myleads"),
    path('leads-detail/', views.leadsDetail, name="leads-detail"),
    path('update_contact', views.updateContact, name="update_contact"), #delete when not used
    path('updateStatus_ajax/', views.updateStatus_ajax, name="updateStatus_ajax"),
    path('updateText/', views.UpdateText, name="updateText"),
    path('updateArchived/', views.updateArchived, name="updateArchived"),
    path('updateAssignment/', views.updateAssignment, name="updateAssignment"),



    path('export_filtered_data', views.export_data, name="export_filtered_data"),
    path('export_mylead', views.exportMyleads, name="export_mylead"),
    
    path('createFollowup/', views.createFollowup, name="createFollowup"),
    path('update-followup-status/', views.updateFstatus, name="updateFstatus"),
    path('save-followup-details/', views.saveFDetails, name="saveFDetails"),
    path('updateCLStatus/', views.update_CLStatus, name="update_CLStatus"),

    path('cd-addnotes', views.CloseDealNote, name="cd-addnotes"),
    path('updated_closed', views.updatedClosed, name="updated_closed"),
    path('delete-action/', views.delete_action, name='delete-action'),
]