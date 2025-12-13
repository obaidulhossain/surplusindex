from django.urls import path
from . import views


urlpatterns = [

# Urls for Active Case Search Section

# Urls for Active Skiptracing Section
# path('skiptracing_checklist', views.skiptracing_checklist, name="skiptracing_checklist"),

# Urls for Foreclosure Section
path('add_edit_foreclosure/', views.fclview, name="add_edit_fcl"),
path('filter-fcl', views.filter_foreclosure, name="filter-fcl"),
path("save_notes_ajax/<int:fcl_id>/", views.save_notes_ajax, name="save_notes_ajax"),
path('create_update_fcl', views.update_foreclosure, name="create_update_fcl"),
path("toggle-publish/", views.toggle_publish, name="toggle-publish"),

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
path('def-ajax_search', views.defendant_search, name='def-ajax_search'),



# Urls for Skipptracing Section---------------------------------------------------------------------------
path('skiptrace/', views.skiptrace, name="skiptrace"),
path('mark_as_skiptraced', views.mark_as_skiptraced, name="mark_as_skiptraced"),
path('markas_notfound/',views.saveskiptraceComment, name="markas_notfound"),

    #urls for Create, Edit or Update Contact section
path('create_update_contact', views.CreateUpdateContact, name="create_update_contact"),
path('filter-con', views.filter_contact, name="filter-con"),

    #urls for Mailing Address section
path('fetch_mailing_address', views.fetch_mailing_address, name="fetch_mailing_address"),
path('update_contacts', views.update_contact, name="update_contacts"),#used to update mailing address
path('add_mailing', views.addMailing, name="add_mailing"),
        #Note: search_create_property url is used to search and create mailing address----------

path('update_email', views.update_email, name="update_email"),
path('search_create_email', views.search_create_email, name="search_create_email"),
path('filteremail', views.filterEmail, name="filteremail"),
path('add_email',views.add_email, name="add_email"),
path('update_email_ajax',views.update_email_ajax, name="update_email_ajax"),
path('delete_email_ajax',views.delete_email_ajax, name="delete_email_ajax"),


path('update_wireless', views.update_wireless, name="update_wireless"),
path('create_wireless', views.create_wireless, name="create_wireless"),
path('filterwireless', views.filterWireless, name="filterwireless"),
path('add_wireless',views.add_wireless, name="add_wireless"),

path('update_landline', views.updateLandline, name="update_landline"),
path('create_landline', views.createLandline, name="create_landline"),
path('filter_landline', views.filterLandline, name="filter_landline"),
path('add_landline', views.addLandline, name="add_landline"),

path('filter_related_contact', views.filter_related_contact, name="filter_related_contact"),
path('create_related_contact', views.create_related_contact, name="create_related_contact"),
path('add_related_contact', views.add_related_contact, name="add_related_contact"),
path('skiptrace_related_contact', views.skiptrace_related_contact, name="skiptrace_related_contact"),

# Urls for Delivered Tasks Section------------------------------------------------------------------------
path('deliveredtasks', views.deliveredtasks, name="deliveredtasks"),
# url for global dynamic save Foreclosures fields
path("update-field/<int:pk>/", views.update_foreclosure_field, name="update_field"),


]