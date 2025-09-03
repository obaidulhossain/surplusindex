from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings
class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Updated')
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
    phone = models.CharField(max_length=17, blank=True)
    user_type = models.CharField(max_length=100, choices=CL_TYPE, null=True, blank=True, default="si_client")
    orders = models.ManyToManyField('Admin_Client.Orders', blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    free_credit_balance = models.IntegerField(default=20)
    purchased_credit_balance = models.IntegerField(default=0)
    Total_credits = models.IntegerField(default=0)
    def update_total_credits(self):
        self.Total_credits = self.free_credit_balance + self.purchased_credit_balance
        self.save()

class UserTransactions(Timelogger):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    number_of_leads = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=10, default='usd')
    has_paid = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)  # NEW
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('failed', 'Failed'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')  # NEW
    SOURCE_CHOICES = [
        ('subscription', 'Subscription'),
        ('payg', 'Pay As You Go'),
    ]
    transaction_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, null=True)  # NEW
    def mark_as_paid(self):
        self.status = 'active'
        self.has_paid = True
        self.save(update_fields=['status', 'has_paid', 'updated_at'])

    def mark_as_failed(self):
        self.status = 'failed'
        self.has_paid = False
        self.save(update_fields=['status', 'has_paid', 'updated_at'])

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.transaction_source}) - {self.status}"



class UserPayment(Timelogger):
    
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    number_of_leads = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=10, default='usd')
    has_paid = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)  # NEW
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('failed', 'Failed'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')  # NEW
    SOURCE_CHOICES = [
        ('subscription', 'Subscription'),
        ('payg', 'Pay As You Go'),
    ]
    transaction_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, null=True)  # NEW
    def mark_as_paid(self):
        self.status = 'active'
        self.has_paid = True
        self.save(update_fields=['status', 'has_paid', 'updated_at'])

    def mark_as_failed(self):
        self.status = 'failed'
        self.has_paid = False
        self.save(update_fields=['status', 'has_paid', 'updated_at'])

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.transaction_source}) - {self.status}"


class CreditUsage(Timelogger):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits_used = models.IntegerField(null=True, blank=True)
    number_of_free = models.IntegerField(null=True, blank=True)
    number_of_purchased = models.IntegerField(null=True, blank=True)
    leads = models.ManyToManyField('propertydata.Status', blank=True)

class SubscriptionPlan(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20,null=True, choices=[
        ("subscription", "Subscription"),
        ("payperlead", "Pay Per Lead"),
    ])
    description = models.TextField(blank=True)
    price_id = models.CharField(max_length=255)  # Stripe Price ID
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default="usd")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 29.99
    lead_number = models.CharField(max_length=10, blank=True, null=True)
    interval = models.CharField(max_length=20, choices=[
        ("month", "Monthly"),
        ("half_yearly", "Half Yearly"),
        ("year", "Yearly"),
    ])
    active = models.BooleanField(default=True)
    brochure = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.amount} {self.currency}/{self.interval})"


class StripeSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    customer_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # active, incomplete, canceled, etc.
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    def is_active(self):
        return self.status == "active"

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
    
class Announcements(Timelogger):
    effective_date = models.DateField()
    detail = models.CharField(max_length=255, blank=True, null=True)
    published = models.BooleanField(default=True)
    