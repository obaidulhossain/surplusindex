from django.contrib import admin
from.models import*

# Register your models here.
@admin.register(ClientSettings)
class ClientSettingsAdmin(admin.ModelAdmin):
    list_display = ("user","manage_sub_show_hidden")

@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = ("state","active")