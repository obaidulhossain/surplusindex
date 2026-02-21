from django.db import models
from django.contrib.auth.models import User
from si_user.models import*
class OperationStat(models.Model):                              #
    created_at = models.DateTimeField(auto_now_add=True)        #
    changed_at = models.DateTimeField(null=True, blank=True)            #
    class Meta:                                                 #
        abstract = True 

class Automation(OperationStat):
    PENDING = 'pending'
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS = (
        (PENDING,'Pending'),
        (ACTIVE,'Active'),
        (CLOSED,'Closed'),
    )
    PAID = 'paid'
    UNPAID = 'unpaid'
    FAILED = 'failed'
    PMTSTATUS = (
        (PAID,'Paid'),
        (UNPAID,'Unpaid'),
        (FAILED,'Failed'),
    )
    client = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    states = models.JSONField(default=list)
    tax = models.BooleanField(default=False)
    mortgage = models.BooleanField(default=False)
    preforeclosure = models.BooleanField(default=False)
    postforeclosure = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    surplus_capped = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    transaction = models.ForeignKey(UserTransactions, on_delete=models.CASCADE, null=True, blank=True)
    expiration = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PMTSTATUS, default='unpaid')
    status = models.CharField(max_length=50, choices=STATUS, default='pending')

    name = models.CharField(max_length=255, null=True,blank=True)
    price_id = models.CharField(max_length=255, null=True,blank=True)
    price_amount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    
    update_interval = models.CharField(max_length=255, null=True,blank=True)