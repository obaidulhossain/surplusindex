from django.contrib import admin
from .models import *

class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user','phone', 'free_credit_balance','purchased_credit_balance','Total_credits')

class UserPaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_customer_id','stripe_checkout_id', 'amount','number_of_leads','has_paid','currency')


admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(UserPayment, UserPaymentAdmin)




