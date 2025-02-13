from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportMixin, ImportMixin
from .models import *
from .resources import ForeclosureEventsResource


@admin.register(foreclosure_Events)
class ForeclosureEventsAdmin(ImportExportModelAdmin):
    # list_display = ('state','county','population')
    resource_class = ForeclosureEventsResource
    list_display = ('state', 'county', 'population','tax_sale_next','tax_sale_updated_to','mortgage_sale_next','mortgage_sale_updated_to')