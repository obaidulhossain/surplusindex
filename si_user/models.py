from django.db import models
from django.contrib.auth.models import User

# Create your models here.
    
class subscription(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    monthly_free_credit = models.IntegerField(default=20)
    purchased_credit_balance = models.IntegerField(default=0)
    pay_as_you_go = models.BooleanField(default=False)
