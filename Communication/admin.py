from django.contrib import admin
from .models import*
# Register your models here.
@admin.register(MailAccount)
class MailAccountAdmin(admin.ModelAdmin):
    list_display = ('name','email_address')





@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email','phone')


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('id','name')



@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id','name','subject')

@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = ('sender','scope','custom_subject','send_time','status')

@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ('account', 'received_at','uid', 'sender','recipient', 'thread_key')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name','subject','custom_subject','scheduled_time','status')


