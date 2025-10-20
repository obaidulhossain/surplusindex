from django.contrib import admin
from .models import*
# Register your models here.
@admin.register(CustomExportOptions)
class CustomExportOptionsAdmin(admin.ModelAdmin):
    list_display = ('client_name','client_email', 'number_delivery', 'next_delivery_date', 'delivery_type', 'contact_align', 'active')

@admin.register(ExportLeadFilter)
class ExportLeadFilterAdmin(admin.ModelAdmin):
    list_display = ('filter_name','state', 'sale_type', 'sale_status', 'surplus_status')