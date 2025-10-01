from django.db import models
from django.contrib.auth.models import User
import hashlib
from django.utils import timezone
from realestate_directory.models import States
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
    
class ClientContact(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=17, null=True, blank=True)
    business_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    preferred_states = models.ManyToManyField(States)
    def __str__(self):
        return f"{self.name} ({self.email})"

class ContactList(models.Model):
    name = models.CharField(max_length=100)
    contacts = models.ManyToManyField(ClientContact)
    def __str__(self):
        return self.name

class MailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    signature = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ScheduledEmail(models.Model):
    SCOPE_CHOICES = [
        ("single", "Single Recipient"),
        ("multiple", "Multiple Recipients"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    sender = models.ForeignKey(MailAccount, on_delete=models.CASCADE)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    recipient = models.EmailField(blank=True, null=True)
    recipients_list = models.TextField(blank=True, null=True)  # comma separated
    contact_list = models.ForeignKey(ContactList, null=True, blank=True, on_delete=models.SET_NULL)
    send_to_clients = models.BooleanField(default=False)
    template = models.ForeignKey(MailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    custom_subject = models.CharField(max_length=200, blank=True, null=True)
    custom_body = models.TextField(blank=True, null=True)
    send_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def get_recipients(self):
        if self.scope == "single" and self.recipient:
            return [self.recipient]
        elif self.scope == "multiple":
            emails = []
            if self.send_to_clients:
                emails += list(User.objects.filter(groups__name="clients").exclude(email="").values_list("email", flat=True))
            if self.contact_list:
                emails += list(self.contact_list.contacts.values_list("email", flat=True))
            if self.recipients_list:
                emails += [e.strip() for e in self.recipients_list.split(",") if e.strip()]
            return list(set(emails))  # unique
        return []

class MailMessage(models.Model):
    account = models.ForeignKey(MailAccount, on_delete=models.CASCADE, related_name="emails")
    uid = models.CharField(max_length=255)  # IMAP UID to avoid duplicates
    subject = models.CharField(max_length=500, blank=True, null=True)
    sender = models.EmailField()
    recipient = models.TextField() # store as comma-separated or JSON
    cc = models.TextField(blank=True, null=True)
    bcc = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(null=True, blank=True) #DATE
    body_plain = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)  # email Message-ID
    in_reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    thread_id = models.CharField(max_length=255, blank=True, null=True)  # conversation tracking
    thread_key = models.CharField(max_length=64, db_index=True, editable=False)
    folder = models.CharField(max_length=20, choices=[("inbox","Inbox"), ("sent","Sent"), ("archive","Archive"), ("important","Important")], default="inbox")
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("queued","Queued"), ("sent","Sent"), ("failed","Failed")], default="queued")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("account", "uid", "folder")
    def __str__(self):
        return f"{self.subject or '(No Subject)'} from {self.sender}"
    def save(self, *args, **kwargs):
        if self.thread_id and not self.thread_key:
            self.thread_key = hashlib.sha1(self.thread_id.encode()).hexdigest()
        super().save(*args, **kwargs)

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