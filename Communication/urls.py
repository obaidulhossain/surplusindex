from django.urls import path
from . import views

urlpatterns = [

#--------------url for settings page--------------------
    #path('communication/',views.Communication, name='communication'),
    path("send/", views.send_mail_view, name="send_mail"),
    
    path("com_dashboard/", views.ComDashboard, name="com_dashboard"),
    path("schedule/", views.schedule_email_view, name="schedule_email"),

    path("client_contacts", views.ComContacts, name="client_contacts"),
    path("update_client_contacts", views.CreateUpdateClientContact, name="update_client_contacts"),
    path("client_contacts/<int:contact_id>/update_preferred_states/", views.manage_preferred_states, name="manage_preferred_states"),


    path("com_inbox/", views.ComInbox, name="com_inbox"),
    path("refresh_emails/", views.RefreshEmails, name="refresh_emails"),
    path("fetch_inbox_full/", views.RefreshInboxFull, name="fetch_inbox_full"),
    path("archive/<int:msg_id>/", views.archive_email, name="archive_email"),
    path("delete/<int:msg_id>/", views.delete_email, name="delete_email"),

    path("conversation/<str:thread_key>/<int:account_id>/", views.conversation_view, name="conversation_view"),
    path("conversation/<str:account_id>/<int:message_id>/reply/", views.send_reply_view, name="send_reply"),
    path("toggle-read/<int:msg_id>/", views.toggle_read_status, name="toggle_read"),
    path("edit-message/<int:msg_id>/", views.edit_message_body, name="edit_message"),

    path("com_sent/", views.ComSent, name="com_sent"),
    path("refresh_sent/", views.RefreshSent, name="refresh_sent"),
    path("fetch_sent_full/", views.RefreshSentFull, name="fetch_sent_full"),
    path("archive_sent/<int:msg_id>/", views.archive_sent, name="archive_sent"),
    path("delete_sent/<int:msg_id>/", views.delete_sent, name="delete_sent"),

    path("com_campaign/", views.ComCampaign, name="com_campaign"),
    path("download_scheduled_email_logs/", views.download_email_logs, name="download_scheduled_email_logs"),
    path("clear_email_logs/", views.clear_email_logs, name="clear_email_logs"),
    
    path("com_templates/", views.ComTemplates, name="com_templates"),
    path("create_update_template/", views.createUpdateTemplate, name="create_update_template"),
    
    path("com_settings/", views.ComSettings, name="com_settings"),
    path('create_update_email_ac/',views.CreateUpdateEmailAc, name="create_update_email_ac"),
    path("delete_email_account/", views.DeleteEmailAccount, name="delete_email_account"),
    path("test-email/<int:pk>/", views.TestEmailAccount, name="test_email_ac"),
    
]