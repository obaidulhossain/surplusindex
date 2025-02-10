from django.contrib import admin
from .models import *



class AuctionCalendarAdmin(admin.ModelAdmin):
    list_display = ('state', 'county', 'population','tax_sale_next','tax_sale_updated_to','mortgage_sale_next','mortgage_sale_updated_to')


admin.site.register(foreclosure_Events, AuctionCalendarAdmin)