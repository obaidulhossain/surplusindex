from django.urls import path
from . import views

urlpatterns = [

#--------------url for settings page--------------------
    path('settings/',views.userSettings, name='settings'),
    path('updateuserDetail/', views.updateUserCredentials, name='updateuserDetail'),
#--------------url for settings page--------------------
    path('profile/', views.userProfile, name='profile'),
    path('subscriptions/',views.userSubscription, name='subscriptions'),
    path('checkout/', views.checkout, name='checkout'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]
#stripe listen --forward-to localhost:8000/stripe_webhook/