from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz
from django.core.mail import EmailMessage
from Communication.models import *
from email.utils import formataddr
import imaplib
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Communication.utils import fetch_folder
class Command(BaseCommand):
    help = "Send scheduled emails that are due"

    def handle(self, *args, **options):
        dhaka_tz = pytz.timezone("Asia/Dhaka")
        local = timezone.localtime(timezone.now(), dhaka_tz)  # UTC converted to +06
        now = timezone.now()
        emails = ScheduledEmail.objects.filter(status="pending", send_time__lte=now)

        if not emails.exists():
            self.stdout.write(f"No scheduled emails to send. (Server time: {now}) | (Local Time: {local})")
            accounts = MailAccount.objects.all()
            if not accounts.exists():
                self.stdout.write("No mail accounts found.")
                return

            for account in accounts:
                try:
                    success, msg = fetch_folder(account, folder="INBOX.Sent")
                    if success:
                        self.stdout.write(self.style.SUCCESS(
                            f"Sent Folder Updated [{account.email_address}] (Server time: {now} | Local Time: {local})"
                            
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"Error Updating Sent Folder [{account.email_address}] (Server time: {now} | Local Time: {local})"
                        ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Critical Error Updating Sent Folder [{account.email_address}] Failed: {str(e)}"
                        f"(Server time: {now} | Local Time: {local}) "
                    ))
            return

        for email in emails:
            successes = email.success_emails.split(",") if email.success_emails else []
            failures = email.failed_emails.split(",") if email.failed_emails else []
            try:
                sent_folder = "INBOX.Sent"
                imap = imaplib.IMAP4_SSL(email.sender.imap_host, email.sender.imap_port) if email.sender.use_ssl else imaplib.IMAP4(email.sender.imap_host, email.sender.imap_port)
                imap.login(email.sender.username, email.sender.password)
                # Format sender with display name
                from_email = formataddr((email.sender.name, email.sender.email_address))
                html_body = email.custom_body
                plain_body = strip_tags(html_body)
                recipients = email.get_recipients()

                for r in recipients:
                    if r in successes:
                        continue  # already sent before
                    try:
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
                        successes.append(r)
                        if r in failures:
                            failures.remove(r)
                        self.stdout.write(self.style.SUCCESS(f"✓ Sent to {r}"))
                    except Exception as e:
                        if r not in failures:
                            failures.append(r)
                        # failures.append((r, str(e)))
                        self.stdout.write(self.style.ERROR(f"✗ Failed to {r}: {str(e)}"))
                
                imap.logout()
                # Update tracking fields
                email.success_emails = ",".join(set(successes))
                email.failed_emails = ",".join(set(failures))
                email.attempts += 1

                # Final status decision
                if not failures:
                    email.status = "sent"
                elif email.attempts >= 3:
                    email.status = "sent"  # give up after 3 tries
                else:
                    email.status = "pending"  # try again next cron
                email.save()
                
                # Summary log
                self.stdout.write(self.style.SUCCESS(
                    f"\nSummary for email {email.id}: "
                    f"{len(successes)} sent, {len(failures)} failed "
                    f"(Scheduled at {email.send_time}, Sent at {now} | Local Time: {local})"
                ))
                if failures:
                    for addr in failures:
                        self.stdout.write(self.style.ERROR(f"   - Still failing: {addr}"))

            except Exception as e:
                email.status = "failed"
                email.attempts += 1
                email.save()
                self.stdout.write(self.style.ERROR(
                    f"Critical failure for email {email.id}: {str(e)}"
                    f"(Server time: {now} | Local Time: {local}) "
                ))
        accounts = MailAccount.objects.all()
        if not accounts.exists():
            self.stdout.write("No mail accounts found.")
            return

        for account in accounts:
            try:
                success, msg = fetch_folder(account, folder="INBOX.Sent")
                if success:
                    self.stdout.write(self.style.SUCCESS(
                        f"[{account.email_address}] (Server time: {now} | Local Time: {local})"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"[{account.email_address}] (Server time: {now} | Local Time: {local})"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"[{account.email_address}] Failed: {str(e)}"
                    f"(Server time: {now} | Local Time: {local}) "
                ))
