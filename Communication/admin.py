from django.contrib import admin
from .models import*
# Register your models here.
@admin.register(MailAccount)
class MailAccountAdmin(admin.ModelAdmin):
    list_display = ('name','email_address')

@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ('account', 'received_at','uid', 'sender','recipient', 'thread_key')