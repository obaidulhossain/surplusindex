from django.contrib import admin
from .models import *
from si_user.models import *

class OrdersAdmin(admin.ModelAdmin):
    list_display = ('get_users','date_ordered','order_detail', 'order_status','payment_status')
    list_filter = ('order_status', 'payment_status', 'date_ordered')
    search_fields = ('order_detail',)

    def get_users(self, obj):
        # Access users through UserDetail and return their usernames
        users = UserDetail.objects.filter(orders=obj)
        return ", ".join([user.user.username for user in users])
    get_users.short_description = "Associated Users"

class DeliveriesAdmin(admin.ModelAdmin):
    list_display = ('order_id','delivery_date', 'delivery_status','delivery_note')
    list_filter = ('delivery_date', 'delivery_status')
    search_fields = ('delivery_note',)
    def order_id(self, obj):
        # Access users through UserDetail and return their usernames
        orders = Orders.objects.filter(deliveries=obj)
        return "order.id".join([str(order.id) for order in orders])
    order_id.short_description = "Associated Order"

admin.site.register(Orders, OrdersAdmin)
admin.site.register(Deliveries, DeliveriesAdmin)