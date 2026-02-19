from django.urls import path
from . import views


urlpatterns = [
    path('', views.Automate, name="automate"),
    # path("direct-subscribe/", views.direct_subscribe, name="direct-subscribe"),
    path("update/<int:pk>/", views.update_automation_field),
    path("update-state/<int:pk>/", views.update_automation_state),
    path("update-subscription/<int:pk>/", views.update_subscription),
    path("pay/<int:pk>/", views.pay_automation, name="pay_automation"),
]