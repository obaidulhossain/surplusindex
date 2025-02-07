from django.urls import path
from . import views




urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard" ),
    path('add/', views.addProperty, name="addproperty"),
    path('leads/', views.allLeads, name="leads"),
    path('myleads/', views.myLeads, name="myleads"),
    path('buy-leads', views.addtoMyList, name="buy-leads"),
    path('hide-leads', views.hidefromallLeads, name="hide-leads"),
    path('unhide-leads', views.unhideLeads, name="unhide-leads"),
    path('hidden-leads/', views.hiddenLeads, name='hidden-leads'),
    path('archived/', views.archivedLeads, name="archived"),
    path('archive', views.archive_mylead, name="archive"),
    path('unarchive', views.unarchive_mylead, name="unarchive")
]