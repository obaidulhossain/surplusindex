from django.db import models
from django.contrib.auth.models import User

# Create your models here.
    
# class subscription(models.Model):
#     user_name = models.ForeignKey(User, on_delete=models.CASCADE)
#     monthly_free_credit = models.IntegerField(default=20)
#     pay_as_you_go = models.BooleanField(default=False)

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='credits')
    phone = models.CharField(max_length=12, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    free_credit_balance = models.IntegerField(default=20)
    purchased_credit_balance = models.IntegerField(default=0)
    Total_credits = models.IntegerField(default=0)
    def update_total_credits(self):
        self.total_credits = self.free_credit_balance + self.purchased_credit_balance
        self.save()


class UserPayment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_leads = models.IntegerField()
    currency = models.CharField(max_length=3)
    has_paid = models.BooleanField(default=False)
    # def __str__(self):
    #     return f"{self.user.username} - {self.product_name} - Paid: {self.has_paid}"

