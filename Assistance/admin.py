from django.contrib import admin
from .models import*

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id','client','title', 'status')

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ('id','sender','text', 'is_seen','is_replied')
# Register your models here.
