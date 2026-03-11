# process_custom_exports.py
from django.core.management.base import BaseCommand
from Automation.models import *
from propertydata.models import Status
from Automation.resources import CustomExportResource
from django.utils import timezone

from datetime import timedelta, date
import calendar

from django.core.mail import EmailMessage
from django.conf import settings
import traceback
class Command(BaseCommand):
    help = "Processes Automation delivery."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        due_exports = Automation.objects.filter(status=Automation.ACTIVE)


        if not due_exports.exists():
            self.stdout.write(self.style.WARNING("No Active Automations."))
            return

        for export_option in due_exports:
            #self.stdout.write(f"Processing export for: {export_option.client_name} ({export_option.client_email})")
            self.stdout.write(f"Processing delivery for: {export_option.client.username} ({export_option.client.email})")
            attachments = []
            userdetail = UserDetail.objects.get(user = export_option.client)

            if export_option.preforeclosure:
                try:
                    queryset = export_option.pre_f_to_deliver.all()
                    if queryset.exists():
                        delivery = AutomationDeliveries.objects.create(automation=export_option,client=export_option.client,list_type=AutomationDeliveries.PREFORECLOSURE)
                        userdetail.pre_foreclosure_delivered.add(*queryset)
                        for fcl in queryset:
                            status, created = Status.objects.get_or_create(lead=fcl, client=export_option.client)
                            fcl.purchased_by.add(export_option.client)
                            delivery.data.add(status)
                        list_name = "Pre-Foreclosure"
                        resource = CustomExportResource(export_option, queryset, list_name)
                        filename, buffer, df = resource.export_to_excel()
                        attachments.append((filename, buffer.getvalue()))
                        delivery.delivered = True
                        delivery.save()
                        export_option.pre_f_to_deliver.clear()
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ No Pre Foreclosure leads to be delivered — skipping attachment."))
                except Exception as e:
                    self.stdout.write(f"❌ Pre Foreclosure Processing Failed : {repr(e)}")
            
            if export_option.postforeclosure:
                try:
                    queryset = export_option.post_f_to_deliver.all()
                    if queryset.exists():
                        delivery = AutomationDeliveries.objects.create(automation=export_option,client=export_option.client,list_type=AutomationDeliveries.POSTFORECLOSURE)
                        userdetail.post_foreclosure_delivered.add(*queryset)
                        for fcl in queryset:
                            status, created = Status.objects.get_or_create(lead=fcl, client=export_option.client)
                            fcl.purchased_by.add(export_option.client)
                            delivery.data.add(status)
                        list_name = "Post-Foreclosure"
                        resource = CustomExportResource(export_option, queryset, list_name)
                        filename, buffer, df = resource.export_to_excel()
                        attachments.append((filename, buffer.getvalue()))
                        delivery.delivered = True
                        delivery.save()                       
                        export_option.post_f_to_deliver.clear()
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ No Post Foreclosure leads to be delivered — skipping attachment."))
                except Exception as e:
                    self.stdout.write(f"❌ Post Foreclosure Processing Failed : {repr(e)}")
            
            if export_option.verified:
                try:
                    queryset = export_option.verified_s_to_deliver.all()
                    if queryset.exists():
                        delivery = AutomationDeliveries.objects.create(automation=export_option,client=export_option.client,list_type=AutomationDeliveries.VERIFIEDSURPLUS)
                        userdetail.verified_surplus_delivered.add(*queryset)
                        for fcl in queryset:
                            status, created = Status.objects.get_or_create(lead=fcl, client=export_option.client)
                            fcl.purchased_by.add(export_option.client)
                            delivery.data.add(status)
                        list_name = "Verified Surplus"
                        resource = CustomExportResource(export_option, queryset, list_name)
                        filename, buffer, df = resource.export_to_excel()
                        attachments.append((filename, buffer.getvalue()))
                        delivery.delivered = True
                        delivery.save()
                        export_option.verified_s_to_deliver.clear()
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ No Verified Surplus leads to be delivered — skipping attachment."))
                except Exception as e:
                    self.stdout.write(f"❌ Verified Surplus Processing Failed : {repr(e)}")

            if attachments:
                email = EmailMessage(
                    subject=f"New List From SurplusIndex Automation",
                    body=f"Hello {export_option.client.username},\n\nNew list arrived from your SurplusIndex Automation.\n\n\n\nRegards,\nSurplusIndex Team\nDate:{today}",
                    # from_email="no-reply@surplusindex.com",
                    # from_email=settings.DEFAULT_FROM_EMAIL,
                    from_email="SurplusIndex List <contact@surplusindex.com>",
                    to=["obaidulbiplob.bd@gmail.com"],
                    )
                for filename, filedata in attachments:
                    email.attach(filename, filedata, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                email.send(fail_silently=False)
            else:
                email = EmailMessage(
                    subject=f"SurplusIndex Automation Delivery Issue {export_option.client.username}",
                    body=f"Date:{today}\nUsername: {export_option.client.username}\nEmail: {export_option.client.email},\n\nNo list delivered. Emmergency action needed.",
                    # from_email="no-reply@surplusindex.com",
                    # from_email=settings.DEFAULT_FROM_EMAIL,
                    from_email="No List Delivered <contact@surplusindex.com>",
                    to=["obaidulbiplob.bd@gmail.com"],
                    )
                email.send(fail_silently=False)