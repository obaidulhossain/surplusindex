from django.db import models
from django.contrib.auth.models import User


class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Updated')
    class Meta:
        abstract = True

class Conversation(Timelogger):
    client=models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations", null=True)
    title = models.CharField(max_length=255, default="Chat with SurplusIndex")
    status = models.CharField(choices=[("open","Open"),("closed","Closed"),], max_length=20, default="open")
    # messages = models.ManyToManyField(Messages, name=True)
    def unseen_messages_count(self):
        return self.messages.filter(
            sender_type="user",
            is_seen=False
        ).count()
    def __str__(self):
        return f"{self.client.username} - {self.title}"



class Messages(Timelogger):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages", null=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_type = models.CharField(max_length=10,choices=[("user", "User"),("admin", "Admin"),("system", "System"),], null=True)
    text = models.TextField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    attachment = models.URLField(blank=True, null=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    










