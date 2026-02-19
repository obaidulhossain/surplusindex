from django.contrib import admin
from .models import *


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ('id', 'tax', 'mortgage', 'preforeclosure', 'postforeclosure', 'verified')
    list_filter = ('tax', 'mortgage', 'preforeclosure', 'postforeclosure', 'verified')