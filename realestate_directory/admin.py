from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportMixin, ImportMixin
from .models import *
from .resources import ForeclosureEventsResource


@admin.register(foreclosure_Events)
class ForeclosureEventsAdmin(ImportExportModelAdmin):
    # list_display = ('state','county','population')
    resource_class = ForeclosureEventsResource
    list_display = ('state', 'county', 'population','sale_type','event_next','event_updated_from','event_updated_to')