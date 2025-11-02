from django.db import models
from propertydata.models import Foreclosure

# Create your models here.
class CustomDeliveryClients(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email =models.EmailField()
    contact_align = models.CharField(choices=[
        ("horizontal","Horizontal"),
        ("vertical","Vertical")
    ], max_length=20, default="horizontal")
    pre_foreclosure = models.ManyToManyField(Foreclosure, related_name="pref_delivered")
    post_foreclosure = models.ManyToManyField(Foreclosure, related_name="postf_delivered")
    verified_surplus = models.ManyToManyField(Foreclosure, related_name="vf_delivered")
    old_leads = models.ManyToManyField(Foreclosure, related_name="old_leads")
    columns = models.JSONField(default=list, help_text="List of field names in desired order")
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name or self.email


class ExportLeadFilter(models.Model):
    filter_name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    sale_type = models.CharField(max_length=255,blank=True, null=True)
    sale_status = models.CharField(max_length=255,blank=True, null=True)
    surplus_status = models.CharField(max_length=255,blank=True, null=True)
    def __str__(self):
        return f"{self.filter_name} - {self.state} - {self.sale_type} - {self.sale_status} - {self.surplus_status}"
    
class CustomExportOptions(models.Model):
    client = models.ForeignKey(CustomDeliveryClients, on_delete=models.CASCADE, null=True,blank=True)
    client_name = models.CharField(max_length=255, default="Default Template")
    client_email = models.EmailField()
    number_delivery = models.IntegerField()
    next_delivery_date = models.DateField(null=True)
    delivery_type = models.CharField(choices=[
        ("pre-foreclosure","Pre-Foreclosure"),
        ("post-foreclosure","Post-Foreclosure"),
        ("verified","Verified")
    ], max_length=20, default="verified")
    contact_align = models.CharField(choices=[
        ("horizontal","Horizontal"),
        ("vertical","Vertical")
    ], max_length=20, default="horizontal")
    pre_foreclosure = models.ManyToManyField(Foreclosure, related_name="pre_delivered")
    post_foreclosure = models.ManyToManyField(Foreclosure, related_name="post_delivered")
    verified_surplus = models.ManyToManyField(Foreclosure, related_name="verified_delivered")
    old_leads = models.ManyToManyField(Foreclosure, related_name="not_delivered")
    filter_option = models.ManyToManyField(ExportLeadFilter)
    columns = models.JSONField(default=list, help_text="List of field names in desired order")
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.client_name} - {self.delivery_type}"

