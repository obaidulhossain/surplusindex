from django.shortcuts import render
from .models import*
import stripe
import json
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required


stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
def Automate(request):
    automations = Automation.objects.all()
    context={
        "automations":automations,
    }
    return render(request,"Automation/automate.html",context)





@login_required
def direct_subscribe(request):
    if request.method == "POST":
        data = json.loads(request.body)
        automation_id = data.get("automation_id")

        automation = Automation.objects.get(id=automation_id)
        user = request.user
        customer_id = user.credits.stripe_customer_id

        try:
            # Create subscription and charge default payment method
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": automation.price_id}],
                expand=["latest_invoice.payment_intent"],
            )

            return JsonResponse({
                "status": "success",
                "subscription_id": subscription.id
            })

        except stripe.error.CardError as e:
            # Card failed → redirect to checkout
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": automation.price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=request.build_absolute_uri("/payment-success/"),
                cancel_url=request.build_absolute_uri("/payment-cancel/"),
            )

            return JsonResponse({
                "status": "redirect_checkout",
                "checkout_url": checkout_session.url
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })