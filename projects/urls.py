from django.urls import path
from . import views


urlpatterns = [
path('events_calendar', views.EventsCalendar, name="events_calendar"),
path('active_tasks', views.ActiveTasks, name="active_tasks"),
path('deliveredtasks', views.deliveredtasks, name="deliveredtasks"),



# Urls for Foreclosure Section

path('add_edit_foreclosure/', views.fclview, name="add_edit_fcl"),
path('filter-fcl', views.filter_foreclosure, name="filter-fcl"),
path('create_update_fcl', views.update_foreclosure, name="create_update_fcl"),




# path('get-property-details/', views.get_property_details, name='get_property_details'),
# path('case-number-suggestions/', views.case_number_suggestions, name='case_number_suggestions'),


# views for property section




# views for property section
path('update_prop', views.update_property, name='update_prop'),
path('ajax-search/', views.address_search, name='ajax_search'),
path('add_property', views.fcl_add_property, name='add_property'),
path('search_create_property', views.search_create_property, name='search_create_property'),




# views for flaintiff section
path('create_update_plt', views.create_update_plaintiff, name="create_update_plt"),
path('update_plt', views.update_plaintiff, name='update_plt'),
path('add_plaintiff', views.add_plaintiff, name='add_plaintiff'),
path('plt-ajax-search/', views.plaintiff_search, name='plt-ajax_search'),


#Views for Defendant section
path('search_create_def', views.search_create_defendant, name='search_create_def'),
path('update_def', views.update_defendant, name='update_def'),
path('add_defendant', views.add_defendant, name='add_defendant'),
path('def-ajax_search', views.defendant_search, name='def-ajax_search')
]