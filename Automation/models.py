from django.db import models
class OperationStat(models.Model):                              #
    created_at = models.DateTimeField(auto_now_add=True)        #
    changed_at = models.DateTimeField(null=True, blank=True)            #
    class Meta:                                                 #
        abstract = True 

class Automation(OperationStat):
    name = models.CharField(max_length=255, null=True,blank=True)
    state = models.CharField(max_length=255, null=True,blank=True)
    price_id = models.CharField(max_length=255, null=True,blank=True)
    price_amount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    tax = models.BooleanField(default=False)
    mortgage = models.BooleanField(default=False)
    preforeclosure = models.BooleanField(default=False)
    postforeclosure = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    update_interval = models.CharField(max_length=255, null=True,blank=True)