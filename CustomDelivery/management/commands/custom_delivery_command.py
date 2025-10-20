from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from propertydata.models import Foreclosure
from CustomDelivery.resources import DynamicDeliveryResource
from CustomDelivery.models import CustomExportOptions
import tempfile

class Command(BaseCommand):
    help = "Send foreclosure leads as Excel attachments to clients."

    def handle(self, *args, **kwargs):
        active_templates = CustomExportOptions.objects.filter(active=True)
        for template in active_templates:
            client = template.client
            self.stdout.write(f"Generating report for {client.email}")

            # Filter leads (customize as needed)
            leads = Foreclosure.objects.filter(active=True)

            # Create dynamic export
            resource = DynamicDeliveryResource(client)
            dataset = resource.export(leads)

            # Save Excel temporarily
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                tmp.write(dataset.xlsx)
                tmp_path = tmp.name

            # Email the file
            subject = "Your Foreclosure Leads Report"
            message = f"Hi {client.username},\n\nYour foreclosure report is attached."
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [client.email])
            email.attach_file(tmp_path)
            email.send()

            self.stdout.write(self.style.SUCCESS(f"Report sent to {client.email}"))
