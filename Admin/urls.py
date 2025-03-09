from django.urls import path
from . import views



urlpatterns = [
    path('new_leads/',views.newly_added_leads, name='new_leads'),
    path('update_assignment', views.assign_leads, name='update_assignment'),
    path('update_case_search_status', views.update_case_search_status, name='update_case_search_status'),
    



]