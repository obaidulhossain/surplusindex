from django.contrib import admin
from .models import *

class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user','phone', 'free_credit_balance','purchased_credit_balance','Total_credits')

class UserPaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_customer_id','stripe_checkout_id', 'amount','number_of_leads','has_paid','currency')

class CreditUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits_used', 'number_of_free', 'number_of_purchased')

admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(UserPayment, UserPaymentAdmin)
admin.site.register(CreditUsage, CreditUsageAdmin)




