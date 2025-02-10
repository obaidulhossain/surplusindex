from django.urls import path
from . import views

urlpatterns = [

    path('auction_calendar/',views.auctionCalendar, name='auction_calendar'),
    path('update-row/', views.update_row, name='update_row'),
    # path('update-date/', views.update_event, name='update_event_date'),
    path('calendar_settings/',views.calendarSettings, name='calendar_settings'),
]