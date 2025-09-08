from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings
class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Updated')
    class Meta:
        abstract = True

class GeneralSettings(Timelogger):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allusers")
    sidebar_expanded = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.user.username}'s Settings"


class ClientSettings(Timelogger):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clients")
    alldata_show_filter = models.BooleanField(default=True)
    purchased_show_filter = models.BooleanField(default=True)
    purchased_show_prospecting_filter = models.BooleanField(default=True)

    manage_sub_show_hidden = models.BooleanField(default=False)
    def __str__(self):
        return f"Client: {self.user.username}'s Settings"