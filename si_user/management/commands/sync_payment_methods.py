import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from si_user.models import UserDetail

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = "Sync payment_method field with Stripe data"

    def handle(self, *args, **kwargs):
        users = UserDetail.objects.exclude(stripe_customer_id__isnull=True).exclude(stripe_customer_id__exact="")

        for user_detail in users:
            try:
                payment_methods = stripe.PaymentMethod.list(
                    customer=user_detail.stripe_customer_id,
                    type="card",
                )

                if payment_methods.data:
                    card = payment_methods.data[0]
                    exp_month = card.card.exp_month
                    exp_year = card.card.exp_year

                    from datetime import datetime
                    now = datetime.now()

                    if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                        user_detail.payment_method = UserDetail.EXPIRED
                    else:
                        user_detail.payment_method = UserDetail.ADDED
                else:
                    user_detail.payment_method = UserDetail.NOT_ADDED

                user_detail.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {user_detail.user.username} → {user_detail.payment_method}"
                    )
                )

            except stripe.error.StripeError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Stripe error for {user_detail.user.username}: {str(e)}"
                    )
                )