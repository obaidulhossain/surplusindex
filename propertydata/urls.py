from django.urls import path
from . import views




urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard" ),

    path('archived/', views.archivedLeads, name="archived"),
    path('archive', views.archive_mylead, name="archive"),
    path('unarchive', views.unarchive_mylead, name="unarchive"),
]