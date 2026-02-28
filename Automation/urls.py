from django.urls import path
from . import views


urlpatterns = [
    path('', views.Automate, name="automate"),
    # path("direct-subscribe/", views.direct_subscribe, name="direct-subscribe"),
    path("update/<int:pk>/", views.update_automation_field),
    path("update-state/<int:pk>/", views.update_automation_state),
    path("update-subscription/<int:pk>/", views.update_subscription),
    # path("pay/<int:pk>/", views.pay_automation, name="pay_automation"),
    # path("billing/payment-methods/", views.list_payment_methods),
    path("get-payment-options/",views.get_payment_options,name="get_payment_option"),
    path("create/",views.create_subscription,name="create_automation"),

    path('manage_automation', views.ManageAutomation, name="manage_automation"),
    path('manage_automation/stop/', views.stop_automation),
    path("manage_automation/update-setting/", views.update_automation_setting),
]