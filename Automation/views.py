from django.shortcuts import render
from .models import*
import stripe
import json
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from AllSettings.models import Coverage
from django.views.decorators.csrf import csrf_exempt
from authentication.decorators import card_required
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
@card_required
def Automate(request):
    states = Coverage.objects.filter(active=True).order_by("state")
    active_automation = Automation.objects.filter(client = request.user, status = Automation.ACTIVE)
    pending_automation = Automation.objects.filter(client = request.user, status = Automation.PENDING)
    closed_automation = Automation.objects.filter(client = request.user, status = Automation.CLOSED)
    p_Starter = SubscriptionPlan.objects.get(name__iexact="Starter")
    p_Growth = SubscriptionPlan.objects.get(name__iexact="Growth")
    p_Professional = SubscriptionPlan.objects.get(name__iexact="Professional")
    p_Ultimate = SubscriptionPlan.objects.get(name__iexact="Ultimate")
    if pending_automation:
        automation = pending_automation.first()
    elif active_automation:
        automation = active_automation.first()
    else:
        automation = Automation.objects.create(client = request.user)
    
        automation
    context={
        "states":states,
        "automation":automation,
        "p_Starter":p_Starter,
        "p_Growth":p_Growth,
        "p_Professional":p_Professional,
        "p_Ultimate":p_Ultimate,
    }
    return render(request,"Automation/automate.html",context)

@csrf_exempt
def update_automation_field(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")

        automation = Automation.objects.get(pk=pk)

        if not hasattr(automation, field):
            return JsonResponse({"error": "Invalid field"}, status=400)

        model_field = automation._meta.get_field(field)

        # Boolean normalization
        if isinstance(model_field, models.BooleanField):
            value = bool(value)

        setattr(automation, field, value)
        automation.save()

        return JsonResponse({"success": True})

    except Automation.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
    
@csrf_exempt
def update_automation_state(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:
        data = json.loads(request.body)
        state = data.get("state")
        checked = data.get("checked")

        automation = Automation.objects.get(pk=pk)

        states_list = automation.states or []

        if checked:
            if state not in states_list:
                states_list.append(state)
        else:
            if state in states_list:
                states_list.remove(state)

        automation.states = states_list
        automation.save()

        return JsonResponse({"success": True})

    except Automation.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
@csrf_exempt
def update_subscription(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:
        data = json.loads(request.body)
        sub_id = data.get("sub_id")
        checked = data.get("checked")
        automation = Automation.objects.get(pk=pk)
        if checked:
            try:
                subscription = SubscriptionPlan.objects.get(pk=sub_id)
                automation.subscription = subscription
                automation.save()
                return JsonResponse({"success": True})
            except SubscriptionPlan.DoesNotExist:
                return JsonResponse({"error": "Subscription plan not found"}, status=404)       
    except Automation.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

# @login_required
# def direct_subscribe(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         automation_id = data.get("automation_id")

#         automation = Automation.objects.get(id=automation_id)
#         user = request.user
#         customer_id = user.credits.stripe_customer_id

#         try:
#             # Create subscription and charge default payment method
#             subscription = stripe.Subscription.create(
#                 customer=customer_id,
#                 items=[{"price": automation.price_id}],
#                 expand=["latest_invoice.payment_intent"],
#             )

#             return JsonResponse({
#                 "status": "success",
#                 "subscription_id": subscription.id
#             })

#         except stripe.error.CardError as e:
#             # Card failed → redirect to checkout
#             checkout_session = stripe.checkout.Session.create(
#                 customer=customer_id,
#                 payment_method_types=["card"],
#                 line_items=[{
#                     "price": automation.price_id,
#                     "quantity": 1,
#                 }],
#                 mode="subscription",
#                 success_url=request.build_absolute_uri("/payment-success/"),
#                 cancel_url=request.build_absolute_uri("/payment-cancel/"),
#             )

#             return JsonResponse({
#                 "status": "redirect_checkout",
#                 "checkout_url": checkout_session.url
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": str(e)
#             })

@login_required
def pay_automation(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:
        automation = Automation.objects.get(pk=pk, client=request.user)

        if not automation.subscription:
            return JsonResponse({"error": "Select a plan first"})

        # Get Stripe customer id (you already store this)
        customer_id = request.user.credits.stripe_customer_id

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price": automation.subscription.price_id
            }],
            expand=["latest_invoice.payment_intent"],
            metadata={
                "automation_id": automation.id,
                "user_id": request.user.id,
                "product_type": "automation"
            }
        )

        # Save stripe subscription id
        automation.name = automation.subscription.name
        automation.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"error": str(e)})