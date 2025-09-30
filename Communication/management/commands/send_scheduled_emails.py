from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz
from django.core.mail import EmailMessage
from Communication.models import *
from email.utils import formataddr
import imaplib
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
class Command(BaseCommand):
    help = "Send scheduled emails that are due"

    def handle(self, *args, **options):
        dhaka_tz = pytz.timezone("Asia/Dhaka")
        local = timezone.localtime(timezone.now(), dhaka_tz)  # UTC converted to +06
        now = timezone.now()
        emails = ScheduledEmail.objects.filter(status="pending", send_time__lte=now)

        if not emails.exists():
            self.stdout.write(f"No scheduled emails to send. (Server time: {now}) | (Local Time: {local})")
            return

        for email in emails:
            try:
                sent_folder = "INBOX.Sent"
                imap = imaplib.IMAP4_SSL(email.sender.imap_host, email.sender.imap_port) if email.sender.use_ssl else imaplib.IMAP4(email.sender.imap_host, email.sender.imap_port)
                imap.login(email.sender.username, email.sender.password)
                # Format sender with display name
                from_email = formataddr((email.sender.name, email.sender.email_address))
                html_body = email.custom_body
                plain_body = strip_tags(html_body)
                for r in email.get_recipients():
                    # msg = EmailMessage(
                    #     subject=email.custom_subject,
                    #     body=email.custom_body,
                    #     from_email=from_email,
                    #     to=[r],
                    #     reply_to=[email.sender.email_address],
                    # )
                    msg = EmailMultiAlternatives(
                        subject=email.custom_subject,
                        body=plain_body,  # fallback plain text
                        from_email=from_email,
                        to=[r],
                        reply_to=[email.sender.email_address],
                    )

                    # Attach HTML version
                    msg.attach_alternative(html_body, "text/html")
                    msg.send(fail_silently=False)
                    raw_message = msg.message().as_bytes()
                    imap.append(sent_folder, "\\Seen", None, raw_message)

                email.status = "sent"
                email.save()
                imap.logout()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Sent email to {email.get_recipients()}"
                    f"(Scheduled at {email.send_time}, Sent at {now} | Local Time: {local})"
                ))

            except Exception as e:
                email.status = "failed"
                email.save()
                self.stdout.write(self.style.ERROR(
                    f"Failed to send email {email.id}: {str(e)}"
                    f"(Server time: {now} | Local Time: {local}) "
                ))
