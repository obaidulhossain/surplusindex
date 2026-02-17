from django.contrib import admin
from .models import *


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'price_amount', 'tax', 'mortgage', 'preforeclosure', 'postforeclosure', 'verified')
    list_filter = ('name', 'state', 'price_amount', 'tax', 'mortgage', 'preforeclosure', 'postforeclosure', 'verified')