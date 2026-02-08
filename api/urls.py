from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views.auth import *
from api.views.leads import *
urlpatterns = [
    # JWT Auth
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', me, name='me'),
    path('mobile/leads/', leads_list, name='mobile_leads'),
]