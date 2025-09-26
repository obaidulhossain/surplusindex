from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz
from django.core.mail import EmailMessage
from Communication.models import *

class Command(BaseCommand):
    help = "Send scheduled emails that are due"

    def handle(self, *args, **options):
        dhaka_tz = pytz.timezone("Asia/Dhaka")
        now = timezone.localtime(timezone.now(), dhaka_tz)  # UTC converted to +06
        #now = timezone.now()
        emails = ScheduledEmail.objects.filter(status="pending", send_time__lte=now)

        if not emails.exists():
            self.stdout.write(f"No scheduled emails to send. (Server time: {now})")
            return

        for email in emails:
            try:
                for r in email.get_recipients():
                    msg = EmailMessage(
                        subject=email.custom_subject,
                        body=email.custom_body,
                        from_email=email.sender.email_address,
                        to=[r],
                    )
                    msg.send(fail_silently=False)

                email.status = "sent"
                email.save()

                self.stdout.write(self.style.SUCCESS(
                    f"Sent email to {email.get_recipients()}"
                    f"(Scheduled at {email.send_time}, Sent at {now})"
                ))

            except Exception as e:
                email.status = "failed"
                email.save()
                self.stdout.write(self.style.ERROR(
                    f"Failed to send email {email.id}: {str(e)}"
                    f"(Server time: {now})"
                ))
