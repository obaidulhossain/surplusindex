from django.urls import path
from . import views

app_name = 'media_manager'

urlpatterns = [
    path('', views.media_library, name='media_library'),
    path('upload/', views.upload_media, name='upload_media'),
    path('delete/<int:media_id>/', views.delete_media, name='delete_media'),
    path('rename/<int:media_id>/', views.rename_media, name='rename_media'),
    path('api/list/', views.media_list_api, name='media_list_api'),
]