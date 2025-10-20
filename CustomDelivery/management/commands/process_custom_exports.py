# process_custom_exports.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import calendar
from CustomDelivery.models import *

class Command(BaseCommand):
    help = "Processes CustomExportOptions and updates next delivery dates if due."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        due_exports = CustomExportOptions.objects.filter(
            active=True,
            next_delivery_date__lte=today
        )

        if not due_exports.exists():
            self.stdout.write(self.style.WARNING("No Pending Deliveries."))
            return

        for export_option in due_exports:
            self.stdout.write(f"Processing export for: {export_option.client_name} ({export_option.client_email})")

            try:
                # STEP 1 — (Later) Generate and email Excel file
                # We'll add this logic after we finish the scheduling foundation.

                # STEP 2 — Calculate next delivery date
                next_date = self.calculate_next_delivery_date(export_option)

                export_option.next_delivery_date = next_date
                export_option.save(update_fields=["next_delivery_date"])

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Updated next delivery date for {export_option.client_name} → {next_date}"
                ))

            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"❌ Failed for {export_option.client_name}: {str(e)}"
                ))

    def calculate_next_delivery_date(self, export_option):
        """
        Calculate the next delivery date based on number_delivery.
        Example:
            number_delivery = 4 → next delivery = today + 7 days (≈ 30/4)
        """
        today = timezone.now().date()
        deliveries_per_month = export_option.number_delivery or 1

        # Get current month info
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]

        # Generate the delivery days of this month
        interval = days_in_month / deliveries_per_month
        delivery_days = [
            int(round(interval * i)) for i in range(1, deliveries_per_month + 1)
        ]
        # Find next delivery day in this month
        for day in delivery_days:
            if day > today.day:
                # Found the next delivery in this month
                return date(year, month, min(day, days_in_month))

        # If no days left in this month → go to next month's first delivery
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        next_month_days = calendar.monthrange(next_year, next_month)[1]
        next_interval = next_month_days / deliveries_per_month
        next_delivery_day = int(round(next_interval))  # 1st delivery slot of next month

        return date(next_year, next_month, min(next_delivery_day, next_month_days))

