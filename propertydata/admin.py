from django.contrib import admin
from .models import *
 

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

class CourtRecordAdmin(admin.ModelAdmin):
    list_display = ("case_number", "court_name", "case_type", "case_status")

class LandlineAdmin(admin.ModelAdmin):
    list_display = ("l_number", "l_caller_id", "l_status")

class WirelessAdmin(admin.ModelAdmin):
    list_display = ("w_number", "w_caller_id", "w_status")


class EmailAdmin(admin.ModelAdmin):
    list_display = ("email_address", "status")

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'instrument_no', 'amount', 'reference_transaction', 'comment')

class ForeclosureAdmin(admin.ModelAdmin):
    list_display = ('state', 'county', 'sale_date', 'sale_type', 'sale_status', 'sale_price', 'possible_surplus','verified_surplus')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('call_status', 'agreement_status', 'claim_status')


admin.site.register(Property, PropertyAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(Wireless_Number, WirelessAdmin)
admin.site.register(Landline_Number, LandlineAdmin)
admin.site.register(Court_Record, CourtRecordAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Foreclosure, ForeclosureAdmin)
admin.site.register(Status, StatusAdmin)
