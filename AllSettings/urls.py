from django.urls import path
from . import views

urlpatterns = [
    path('save-sidebar-setting/', views.save_sidebar_setting, name='save_sidebar_setting'),
    path("update-show-hide-setting/", views.update_client_filter_display_setting, name="update-show-hide-setting"),
]