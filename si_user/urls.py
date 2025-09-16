from django.urls import path
from . import views

urlpatterns = [

#--------------url for settings page--------------------
    path('settings/',views.userSettings, name='settings'),
    path('updateuserDetail/', views.updateUserCredentials, name='updateuserDetail'),
#--------------url for settings page--------------------
    path('profile/', views.userProfile, name='profile'),
    path('export-usage/<int:usage_id>/', views.export_leads_from_usage, name='export_usage_leads'),

    path('subscriptions/',views.userSubscription, name='subscriptions'),
    path('checkout/', views.checkout, name='checkout'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('subscriptions/cancel/<str:subscription_id>', views.cancel_subscription, name='cancel_subscription'),
    path('subscriptions/pause/', views.pause_subscription, name='pause_subscription'),
    path('subscriptions/resume/', views.resume_subscription, name='resume_subscription'),
    path('subscriptions/extend/', views.extend_subscription, name='extend_subscription'),
    path('hide_show_hidden_subscription',views.HideShow_HiddenSubs, name="hide_show_hidden_subscription"),
    path('subscriptions/hide_show/', views.hide_show_subscription, name='hide_show_subscription'),

    path('settings/password/', views.changePassword, name='changePassword'),
]
#stripe listen --forward-to localhost:8000/stripe_webhook/