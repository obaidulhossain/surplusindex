from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from .resources import ForeclosingEntityResource
 

# Register your models here.

class PropertyAdmin(admin.ModelAdmin):
    list_display = ("state", "county", "parcel", "city", "zip_code", "property_address" )
#    list_filter = ("state", "county", "parcel", "city", "zip_code" )
    def property_address (self, obj):
        return obj.fulladdress
    property_address.admin_order_field = 'house_number'
    property_address.short_description = 'Property Address'
    #    return '{} {}'.format(obj.house_number, obj.road_name, obj.road_type)
    #    return f"{self.house_number} {self.road_name} {self.road_type}"
    
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "middle_name", "last_name", "name_suffix")

# class CourtRecordAdmin(admin.ModelAdmin):
#     list_display = ("case_number", "court_name", "case_type", "case_status")

class LandlineAdmin(admin.ModelAdmin):
    list_display = ("l_number", "l_caller_id", "l_status")

class WirelessAdmin(admin.ModelAdmin):
    list_display = ("w_number", "w_caller_id", "w_status")


class EmailAdmin(admin.ModelAdmin):
    list_display = ("email_address", "status")

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'instrument_no', 'amount', 'reference_transaction', 'comment')

class ForeclosureAdmin(admin.ModelAdmin):
    list_display = ('id', 'published', 'state', 'county', 'case_number', 'case_search_assigned_to', 'sale_date', 'sale_type', 'sale_status','surplus_status', 'sale_price', 'possible_surplus','verified_surplus')
    list_filter = ('state', 'county', 'sale_type', 'sale_status','surplus_status','published', 'case_search_status')
    #search_fields = ()

class StatusAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'lead_id','find_contact_status', 'skiptracing_status', 'call_status','negotiation_status','closing_status')
    

admin.site.register(Property, PropertyAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(Wireless_Number, WirelessAdmin)
admin.site.register(Landline_Number, LandlineAdmin)
# admin.site.register(Court_Record, CourtRecordAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Foreclosure, ForeclosureAdmin)
admin.site.register(Status, StatusAdmin)




@admin.register(ForeclosingEntity)
class ForeclosingEntityAdmin(ImportExportModelAdmin):
    resource_class = ForeclosingEntityResource
    list_display = ('individual_name', 'business_name', 'dba')