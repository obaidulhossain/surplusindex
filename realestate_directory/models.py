from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class directoryData(models.Model):
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    recorder = models.URLField(blank=True)
    assessor = models.URLField(blank=True)
    tax_collector = models.URLField(blank=True)
    gis = models.URLField(blank=True)
    district = models.URLField(blank=True)
    civil = models.URLField(blank=True)
    municipal = models.URLField(blank=True)
    probate = models.URLField(blank=True)
    superior = models.URLField(blank=True)
    supreme = models.URLField(blank=True)
    surrogate = models.URLField(blank=True)
    public_notice = models.URLField(blank=True)


class foreclosure_Events(models.Model):
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    population = models.IntegerField(blank=True)
    event_site = models.URLField(blank=True)
    sale_type = models.CharField(max_length=100, null=True)
    event_updated_from = models.DateField(blank=True, null=True)
    event_updated_to = models.DateField(blank=True, null=True)
    event_status = models.CharField(max_length=255, blank=True)
    event_case_search = models.URLField(blank=True)
    event_next = models.DateField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    directory = models.ForeignKey(directoryData, on_delete=models.CASCADE, blank=True, null=True)
    

