from django.db import models
from django.contrib.auth.models import User
from si_user.models import*
from propertydata.models import Status

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
    surplus_capped = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True, default=15000)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    enrolled_stripe_subscrption = models.CharField(max_length=255, null=True, blank=True)
    transaction = models.ManyToManyField(UserTransactions)
    expiration = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PMTSTATUS, default='unpaid')
    status = models.CharField(max_length=50, choices=STATUS, default='pending')

    name = models.CharField(max_length=255, null=True,blank=True)
    price_id = models.CharField(max_length=255, null=True,blank=True)
    price_amount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    
    update_interval = models.CharField(max_length=255, null=True,blank=True)

    auto_renew = models.BooleanField(default=True)
    renew_when_expired = models.BooleanField(default=False)
    renew_when_limit = models.BooleanField(default=False)
    pre_f_to_deliver = models.ManyToManyField(Foreclosure, related_name="pre_to_deliver")
    post_f_to_deliver = models.ManyToManyField(Foreclosure, related_name="post_to_deliver")
    verified_s_to_deliver = models.ManyToManyField(Foreclosure, related_name="verified_to_deliver")

class AutomationDeliveries(OperationStat):
    automation = models.ForeignKey(Automation, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data = models.ManyToManyField(Status, related_name="DataDelivered")
    delivered = models.BooleanField(default=False)
    PREFORECLOSURE = 'pre foreclosure'
    POSTFORECLOSURE = 'post foreclosure'
    VERIFIEDSURPLUS = 'verified surplus'
    LISTTYPE = (
        (PREFORECLOSURE,'Pre Foreclosure'),
        (POSTFORECLOSURE,'Post Foreclosure'),
        (VERIFIEDSURPLUS,'Verified Surplus'),
    )
    list_type = models.CharField(max_length=100, choices=LISTTYPE, blank=True, null=True)
