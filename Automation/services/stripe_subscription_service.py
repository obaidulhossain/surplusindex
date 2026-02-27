import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeSubscriptionService:

    def __init__(self, user):
        self.user = user
        self.customer_id = user.credits.stripe_customer_id

    # ---------------------------------
    # PAYMENT METHODS
    # ---------------------------------

    def list_payment_methods(self):
        return stripe.PaymentMethod.list(
            customer=self.customer_id,
            type="card",
        ).data

    def create_setup_intent(self):
        return stripe.SetupIntent.create(
            customer=self.customer_id
        )

    def attach_payment_method(self, payment_method_id):
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=self.customer_id,
        )

        stripe.Customer.modify(
            self.customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            },
        )

    # ---------------------------------
    # SUBSCRIPTION
    # ---------------------------------

    def create_subscription(self, price_id, payment_method_id, metadata):
        self.attach_payment_method(payment_method_id)
        subscription = stripe.Subscription.create(
            customer=self.customer_id,
            items=[{"price": price_id}],
            metadata=metadata or {},
            expand=["latest_invoice.payment_intent"],
        )
        payment_intent = subscription.latest_invoice.payment_intent
        return {
            "subscription": subscription,
            "payment_intent": payment_intent
        }

    def cancel_subscription(self, subscription_id):
        return stripe.Subscription.delete(subscription_id)

    # ---------------------------------
    # RETRY PAYMENT
    # ---------------------------------

    def confirm_payment(self, client_secret):
        return stripe.PaymentIntent.confirm(client_secret)