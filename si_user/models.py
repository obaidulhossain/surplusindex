from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        abstract = True

# from Admin_Client.models import *
# created_at = models.DateTimeField(auto_now_add=True)
# Create your models here.
    
# class subscription(models.Model):
#     user_name = models.ForeignKey(User, on_delete=models.CASCADE)
#     monthly_free_credit = models.IntegerField(default=20)
#     pay_as_you_go = models.BooleanField(default=False)

class UserDetail(Timelogger):
    SI_CLIENT = 'si_client'
    MANUAL_CLIENT = 'manual_client'
    CL_TYPE = (
        (SI_CLIENT, 'SI Client'),
        (MANUAL_CLIENT, 'Manual Client'),
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='credits')
    phone = models.CharField(max_length=12, blank=True)
    user_type = models.CharField(max_length=100, choices=CL_TYPE, null=True, blank=True, default="SI Client")
    orders = models.ManyToManyField('Admin_Client.Orders', blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    free_credit_balance = models.IntegerField(default=20)
    purchased_credit_balance = models.IntegerField(default=0)
    Total_credits = models.IntegerField(default=0)
    def update_total_credits(self):
        self.Total_credits = self.free_credit_balance + self.purchased_credit_balance
        self.save()


class UserPayment(Timelogger):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_leads = models.IntegerField()
    currency = models.CharField(max_length=3)
    has_paid = models.BooleanField(default=False)
    # def __str__(self):
    #     return f"{self.user.username} - {self.product_name} - Paid: {self.has_paid}"

class CreditUsage(Timelogger):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits_used = models.IntegerField(null=True, blank=True, max_length=3)
    number_of_free = models.IntegerField(null=True, blank=True, max_length=3)
    number_of_purchased = models.IntegerField(null=True, blank=True, max_length=3)
    leads = models.ManyToManyField('propertydata.Status', blank=True)