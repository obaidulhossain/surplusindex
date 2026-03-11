from django.urls import path
from . import views


urlpatterns = [
    path('', views.Automate, name="automate"),
    path('admin_automation/', views.AdminAutomation, name="admin_automation"),
    path('admin_manage_automation/', views.AdminManageAutomation, name="admin_manage_automation"),
    path("admin_manage_automation/toggle-post-delivery/",views.toggle_post_delivery,name="toggle_post_delivery"),
    path("admin_manage_automation/toggle_verified_delivery/",views.toggle_verified_delivery,name="toggle_verified_delivery"),
    path("download_automation_leads/",views.download_automation_leads, name="download_automation_leads"),
    path("admin_automation/run-automation-delivery/",views.run_automation_delivery,name="run_automation_delivery",),
    
    # path("direct-subscribe/", views.direct_subscribe, name="direct-subscribe"),
    path("update/<int:pk>/", views.update_automation_field),
    path("update-state/<int:pk>/", views.update_automation_state),
    path("update-subscription/<int:pk>/", views.update_subscription),
    # path("pay/<int:pk>/", views.pay_automation, name="pay_automation"),
    # path("billing/payment-methods/", views.list_payment_methods),
    path("get-payment-options/",views.get_payment_options,name="get_payment_option"),
    path("get-prices/", views.getPrices),

    path("check-installments/", views.check_installments),
    path("create/",views.create_subscription,name="create_automation"),

    path('manage_automation', views.ManageAutomation, name="manage_automation"),
    path('manage_automation/stop/', views.stop_automation),
    path("manage_automation/update-setting/", views.update_automation_setting),
    path("manage_automation/download-data/<int:delivery_id>/", views.download_delivery_data, name="download_delivery_data"),
    path('manage_automation/download-invoice/<str:invoice_id>/',views.download_invoice,name="download_invoice"),
]