from django.urls import path
from . import views

urlpatterns = [
    # ExportLeadFilter CRUD
    path("filters/", views.filter_list, name="filter_list"),
    path("filters/new/", views.filter_create, name="filter_create"),
    path("filters/<int:pk>/edit/", views.filter_update, name="filter_update"),
    path("filters/<int:pk>/delete/", views.filter_delete, name="filter_delete"),

    # CustomExportOptions CRUD
    path("options/", views.export_option_list, name="export_option_list"),
    path("options/new/", views.export_option_create, name="export_option_create"),
    path("options/<int:pk>/edit/", views.export_option_update, name="export_option_update"),
    path("options/<int:pk>/delete/", views.export_option_delete, name="export_option_delete"),
]
