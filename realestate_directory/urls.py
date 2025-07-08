from django.urls import path
from . import views

urlpatterns = [

    path('auction_calendar/',views.auctionCalendar, name='auction_calendar'),
    path('update-row/', views.update_row, name='update_row'),

    # path('update-date/', views.update_event, name='update_event_date'),
    path('calendar_settings/',views.calendarSettings, name='calendar_settings'),
    path('filterevents', views.FilterEvents, name='filterevents'),
    path('delete-event/', views.DeleteEvent, name="delete-event"),

    path('calendar_settings/upload',views.upload_file, name='upload_calendar_data'),
    path('export', views.export_data, name='export_data'),
    # path('calendar_settings/preview-uploaded',views.submit_data, name='submit_data'),
]