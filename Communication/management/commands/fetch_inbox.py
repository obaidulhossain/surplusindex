from django.core.management.base import BaseCommand
from Communication.models import MailAccount
from Communication.utils import *
from django.utils import timezone


class Command(BaseCommand):
    help = "Fetch inbox emails for all mail accounts"

    def handle(self, *args, **options):
        self.stdout.write(f"Running inbox fetch at {timezone.now()}")

        accounts = MailAccount.objects.all()
        if not accounts.exists():
            self.stdout.write("No mail accounts found.")
            return

        for account in accounts:
            try:
                success, msg = fetch_folder_crosscheck(account, folder="INBOX")
                if success:
                    self.stdout.write(self.style.SUCCESS(
                        f"[{account.email_address}] {msg}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"[{account.email_address}] {msg}"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"[{account.email_address}] Failed: {str(e)}"
                ))
