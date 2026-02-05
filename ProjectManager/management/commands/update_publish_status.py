from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.management.base import BaseCommand
from propertydata.models import *
from django.db.models import Q

class Command(BaseCommand):
    help = "Update publish unpublish status."

    def handle(self, *args, **kwargs):
        print("STEP 1: start")
        qs = Foreclosure.objects.filter(
            sale_price__isnull=False,
            fcl_final_judgment__isnull=False,
        ).filter(
            Q(possible_surplus__isnull=True) |
            Q(possible_surplus=Decimal("0"))
        )
        print("STEP 2: qs built")
        updated = 0

        for f in qs:
            try:
                print("STEP 3: loop", f.id)
                float(f.sale_price)
                float(f.fcl_final_judgment)
                f.update_possible_surplus()
                updated += 1
            except (ValueError, TypeError):
                continue
        print(f"STEP 4: after update loop. updated:{updated}")
        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} foreclosure records")
        )
        
        PUBLISH_SALE_STATUSES = [
            Foreclosure.SOLD,
            Foreclosure.ACTIVE,
        ]
        PUBLISH_SURPLUS_STATUSES = [
            Foreclosure.NOT_DETERMINED,
            Foreclosure.POSSIBLE_SURPLUS,
            Foreclosure.NO_POSSIBLE_SURPLUS,
            Foreclosure.FUND_AVAILABLE,
            Foreclosure.MOTION_FILED,
        ]
        to_publish = (
            Foreclosure.objects
            .filter(
                sale_status__in=PUBLISH_SALE_STATUSES,
                surplus_status__in=PUBLISH_SURPLUS_STATUSES,
                defendant__skiptraced=True,   # ✅ at least one skiptraced Contact
                published=False
            )
            .distinct()  # REQUIRED for M2M
        )
        published_count = to_publish.update(published=True)
        self.stdout.write(
            self.style.SUCCESS(f"Published {published_count} foreclosure records.")
        )

        
        UNPUBLISH_SALE_STATUSES = [
            Foreclosure.ACTIVE,
            Foreclosure.SOLD,          
        ]

        UNPUBLISH_SURPLUS_STATUSES = [
            
            Foreclosure.FUND_CLAIMED,
            Foreclosure.NO_SURPLUS,
        ]
        to_unpublish_first = (
            Foreclosure.objects
            .filter(published=True)
            .exclude(
                sale_status__in=PUBLISH_SALE_STATUSES,
            )
        )
        to_unpublish_second = (
            Foreclosure.objects
            .filter(
                published=True,
                sale_status__in=UNPUBLISH_SALE_STATUSES,
                surplus_status__in=UNPUBLISH_SURPLUS_STATUSES,
                )
        )
        unpublished_f = to_unpublish_first.update(published=False)
        unpublished_s = to_unpublish_second.update(published=False)
        unpublished_count = unpublished_f + unpublished_s
        self.stdout.write(
            self.style.WARNING(f"Unpublished {unpublished_count} foreclosure records.")
        )
        
        fix_possible_surplus = Foreclosure.objects.filter(
            possible_surplus__isnull=False,
            surplus_status=Foreclosure.POSSIBLE_SURPLUS,
        ).filter(
            possible_surplus__lt=Decimal("5000")
        )
        fix_possible_surplus_count = fix_possible_surplus.update(surplus_status="no possible surplus")

        fix_no_possible_surplus = Foreclosure.objects.filter(
            possible_surplus__isnull=False,
            surplus_status=Foreclosure.NO_POSSIBLE_SURPLUS,
        ).filter(
            possible_surplus__gte=Decimal("5000")
        )
        fix_no_possible_surplus_count = fix_no_possible_surplus.update(surplus_status="possible surplus")
        today = timezone.now().date()
        try:                
            # STEP 2 — (Optional) Send via email
            email = EmailMessage(
                subject=f"Status Updated - {published_count}/{unpublished_count}",
                body=f"Published: {published_count} \nUnpublished: {unpublished_count}\nStatus Changed to No possible Surplus: {fix_possible_surplus_count} \nStatus Changed to Possible Surplus: {fix_no_possible_surplus_count}  \nDate of action: {today}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["obaidulbiplob.bd@gmail.com"],
            )
            # email.attach(filename, buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            email.send(fail_silently=False)
        except Exception as e:
            self.stdout.write(f"❌ Failed for: {repr(e)}")


