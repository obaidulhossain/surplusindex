from django.contrib import admin
from .models import *

class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user','created_at','changed_at','user_type','phone', 'free_credit_balance','purchased_credit_balance','Total_credits')
    search_fields = ("user")
class UserPaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_customer_id','stripe_checkout_id', 'amount','number_of_leads','has_paid','currency')

class CreditUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits_used', 'number_of_free', 'number_of_purchased')

admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(UserPayment, UserPaymentAdmin)
admin.site.register(CreditUsage, CreditUsageAdmin)

@admin.register(UserTransactions)
class UserTransactionsAdmin(admin.ModelAdmin):
    list_display = ('created_at','changed_at','stripe_customer_id','stripe_checkout_id', 'amount','number_of_leads','has_paid','currency')
    list_filter = ("status", "transaction_source", "has_paid")
    search_fields = ("user", "stripe_customer_id", "stripe_checkout_id", "stripe_subscription_id")

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_id", "amount", "currency", "interval", "active")
    list_filter = ("active", "interval")
    search_fields = ("name", "price_id", "stripe_product_id")


@admin.register(StripeSubscription)
class StripeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('created_at','current_period_end',"user", "plan", "status", "current_period_end", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "subscription_id", "customer_id")


@admin.register(Announcements)
class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ("effective_date", "detail", "published")

