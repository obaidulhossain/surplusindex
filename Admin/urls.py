from django.urls import path
from . import views



urlpatterns = [
    path('all_data/',views.All_Data, name='all_data'),
    path('update_case_assignment', views.assign_leads, name='update_case_assignment'),
    path('update_skp_assignment', views.assign_skiptracing, name='update_skp_assignment'),

    path('update_case_search_status', views.update_case_search_status, name='update_case_search_status'),
    path('update_publish_status', views.update_publish_status, name='update_publish_status'),
    
    path('updatedataStatus', views.updatedataStatus, name='updatedataStatus'),


]