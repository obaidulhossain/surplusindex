from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MailAccount(models.Model):
    name = models.CharField(max_length=100)  # e.g. Contact Mailbox
    email_address = models.EmailField(unique=True)

    # SMTP Settings
    smtp_host = models.CharField(max_length=200)
    smtp_port = models.IntegerField(default=587)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # ⚠️ store encrypted or in a vault
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    # IMAP Settings
    imap_host = models.CharField(max_length=200)
    imap_port = models.IntegerField(default=993)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email_address}>"


class MailMessage(models.Model):
    account = models.ForeignKey(MailAccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.EmailField()
    recipient = models.EmailField()
    message_id = models.CharField(max_length=255, null=True, blank=True)  # IMAP Message-ID
    in_reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    folder = models.CharField(max_length=20, choices=[("inbox","Inbox"), ("sent","Sent")])
    received_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("queued","Queued"), ("sent","Sent"), ("failed","Failed")], default="queued")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_account = models.ForeignKey(MailAccount, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(User, related_name="campaigns")
    scheduled_time = models.DateTimeField()
    status = models.CharField(choices=[
        ("pending","Pending"), 
        ("running","Running"), 
        ("completed","Completed"), 
        ("failed","Failed")
    ], max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

class CampaignEvent(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(choices=[("open","Open"), ("click","Click")], max_length=20)
    url_clicked = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)