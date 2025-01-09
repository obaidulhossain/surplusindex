from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class foreclosure(models.Model):
    fcl_id = models.AutoField(auto_created=True, primary_key=True)
    state = models.CharField(max_length=225)
    county = models.CharField(max_length=225)
    case_no = models.CharField(max_length=225)
    sale_date = models.DateField()
    sale_type = models.CharField(max_length=225)
    sale_status = models.CharField(max_length=225)
    foreclosing_entity = models.CharField(max_length=225)
    defendant = models.CharField(max_length=225)
    additional_party_1 = models.CharField(max_length=225)
    additional_party_2 = models.CharField(max_length=225)
    additional_party_3 = models.CharField(max_length=225)
    additional_party_4 = models.CharField(max_length=225)
    additional_party_5 = models.CharField(max_length=225)
    fcl_final_judgment = models.DecimalField(decimal_places=2, max_digits=10)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10)
    possible_surplus = models.DecimalField(decimal_places=2, max_digits=10)
    verified_surplus = models.DecimalField(decimal_places=2, max_digits=10)
    si_date_listed = models.DateField()
    si_last_updated = models.DateField()
    si_next_update = models.DateField()
    
class subscription(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    monthly_free_credit = models.IntegerField(default=20)
    purchased_credit_balance = models.IntegerField(default=0)
    pay_as_you_go = models.BooleanField(default=False)
