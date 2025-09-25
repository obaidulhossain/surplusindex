from celery import shared_task
from django.core.mail import EmailMessage
from imap_tools import MailBox
from django.utils import timezone
from .models import *
from django.conf import settings

@shared_task
def send_scheduled_email(email_id):
    email_obj = ScheduledEmail.objects.get(id=email_id)
    recipients = email_obj.get_recipients()

    if email_obj.template:
        subject = email_obj.template.subject
        body = f"{email_obj.template.body}\n\n{email_obj.template.signature or ''}"
    else:
        subject = email_obj.custom_subject or ""
        body = email_obj.custom_body or ""

    success_count, fail_count = 0, 0

    for recipient in recipients:
        try:
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=email_obj.sender.email,
                to=[recipient]
            )
            msg.send()
            success_count += 1
        except Exception:
            fail_count += 1

    if fail_count == 0:
        email_obj.status = "sent"
    elif success_count > 0:
        email_obj.status = "partial"
    else:
        email_obj.status = "failed"
    email_obj.save()










@shared_task
def send_mail_task(mail_id):
    try:
        mail = MailMessage.objects.get(id=mail_id)
        account = mail.account

        email = EmailMessage(
            subject=mail.subject,
            body=mail.body,
            from_email=account.email_address,
            to=[mail.recipient],
        )

        # Override SMTP settings dynamically
        email.send(fail_silently=False)

        mail.status = "sent"
        mail.sent_at = timezone.now()
        mail.save()

    except Exception as e:
        mail.status = "failed"
        mail.error_message = str(e)
        mail.save()
        raise





@shared_task
def fetch_emails_task(account_id):
    account = MailAccount.objects.get(id=account_id)

    try:
        with MailBox(account.imap_host).login(account.username, account.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(limit=20, reverse=True):  # fetch last 20 emails
                if not MailMessage.objects.filter(message_id=msg.uid, account=account).exists():
                    MailMessage.objects.create(
                        account=account,
                        subject=msg.subject,
                        body=msg.text or msg.html or "",
                        sender=msg.from_,
                        recipient=account.email_address,
                        message_id=msg.uid,
                        folder="inbox",
                        received_at=msg.date,
                        status="sent",  # incoming is already "sent"
                    )
    except Exception as e:
        print(f"IMAP Fetch Error: {e}")