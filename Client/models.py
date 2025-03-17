from django.db import models
from django.contrib.auth.models import User
from realestate_directory.models import foreclosure_Events

# Create your models here.
class ClientSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.ManyToManyField(foreclosure_Events, related_name='selected_states')
