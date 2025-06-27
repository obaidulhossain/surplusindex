from django.db import models
from django.contrib.auth.models import User
from realestate_directory.models import foreclosure_Events
from propertydata.models import Status

# Create your models here.
class ClientSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.ManyToManyField(foreclosure_Events, related_name='selected_states')

class FollowUp(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FW_STATUS = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    leads = models.ForeignKey(Status, related_name="status_as_lead", on_delete=models.CASCADE)
    followup_date = models.DateField(null=True, blank=True)
    f_note = models.CharField(max_length=255, null=True, blank=True)
    f_result = models.CharField(max_length=255, null=True, blank=True)
    f_status = models.CharField(max_length=255, choices=FW_STATUS)

class ActionHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    lead = models.ForeignKey(Status, on_delete=models.CASCADE)
    action_source = models.CharField(max_length=100, null=True, blank=True)
    action_type = models.CharField(max_length=100, null=True, blank=True)
    action = models.CharField(max_length=100, null=True, blank=True)
    details = models.CharField(max_length=255, null=True, blank=True)
