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
from .services.stripe_subscription_service import StripeSubscriptionService
from django.template.loader import render_to_string
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
    else:
        automation = Automation.objects.create(client = request.user)
    
        automation
    context={
        "states":states,
        "automation":automation,
        "active_automation":active_automation,
        "p_Starter":p_Starter,
        "p_Growth":p_Growth,
        "p_Professional":p_Professional,
        "p_Ultimate":p_Ultimate,
        "STRIPE_PUBLIC_KEY":settings.STRIPE_PUBLISHABLE_KEY,
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




@login_required
def get_payment_options(request):
    service = StripeSubscriptionService(request.user)

    payment_methods = service.list_payment_methods()
    setup_intent = service.create_setup_intent()

    html = render_to_string(
        "partials/payment_methods.html",
        {"payment_methods": payment_methods},
        request=request
    )

    return JsonResponse({
        "html": html,
        "setup_intent": setup_intent.client_secret
    })

@login_required
def create_subscription(request):
    data = json.loads(request.body)
    service = StripeSubscriptionService(request.user)
    automation = Automation.objects.get(client=request.user, status=Automation.PENDING)

    metadata = {
        "product_type": "automation",
        "automation_id": str(automation.id),
        "user_id": str(request.user.id),
    }
    result = service.create_subscription(
        data["price_id"],
        data["payment_method_id"],
        metadata,
    )

    payment_intent = result["payment_intent"]

    if payment_intent.status == "requires_action":
        return JsonResponse({
            "requires_action": True,
            "client_secret": payment_intent.client_secret
        })

    elif payment_intent.status == "succeeded":
        return JsonResponse({"success": True})

    return JsonResponse({
        "error": "Payment failed. Please try again."
    })



# @login_required
# def pay_automation(request, pk):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST only"}, status=400)

#     try:
#         automation = Automation.objects.get(pk=pk, client=request.user)

#         if not automation.subscription:
#             return JsonResponse({"error": "Select a plan first"})

#         # Get Stripe customer id (you already store this)
#         customer_id = request.user.credits.stripe_customer_id

#         # Create subscription
#         subscription = stripe.Subscription.create(
#             customer=customer_id,
#             items=[{
#                 "price": automation.subscription.price_id
#             }],
#             expand=["latest_invoice.payment_intent"],
#             metadata={
#                 "automation_id": automation.id,
#                 "user_id": request.user.id,
#                 "product_type": "automation"
#             }
#         )

#         # Save stripe subscription id
#         automation.name = automation.subscription.name
#         automation.save()

#         return JsonResponse({"success": True})

#     except Exception as e:
#         return JsonResponse({"error": str(e)})

# @login_required
# def pay_automation(request, pk):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST only"}, status=400)

#     try:
#         data = json.loads(request.body)
#         payment_method_id = data.get("payment_method_id")

#         automation = Automation.objects.get(pk=pk, client=request.user)

#         if not automation.subscription:
#             return JsonResponse({"success": False, "error": "Select a plan first"})

#         customer_id = request.user.credits.stripe_customer_id

#         if not payment_method_id:
#             return JsonResponse({"success": False, "error": "No payment method provided"})

#         # Attach payment method to customer (safe even if already attached)
#         stripe.PaymentMethod.attach(
#             payment_method_id,
#             customer=customer_id
#         )

#         # OPTIONAL but recommended:
#         # Set as default for future invoices
#         stripe.Customer.modify(
#             customer_id,
#             invoice_settings={
#                 "default_payment_method": payment_method_id
#             }
#         )

#         # Create subscription using selected payment method
#         subscription = stripe.Subscription.create(
#             customer=customer_id,
#             items=[{
#                 "price": automation.subscription.price_id
#             }],
#             default_payment_method=payment_method_id,
#             expand=["latest_invoice.payment_intent"],
#             metadata={
#                 "automation_id": automation.id,
#                 "user_id": request.user.id,
#                 "product_type": "automation"
#             }
#         )

#         # Check if payment requires action (SCA)
#         payment_intent = subscription["latest_invoice"]["payment_intent"]

#         if payment_intent and payment_intent["status"] == "requires_action":
#             return JsonResponse({
#                 "success": False,
#                 "requires_action": True,
#                 "client_secret": payment_intent["client_secret"]
#             })

#         # Save subscription name (webhook still handles activation)
#         automation.name = automation.subscription.name
#         automation.save()

#         return JsonResponse({"success": True})

#     except stripe.error.CardError as e:
#         return JsonResponse({"success": False, "error": str(e)})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})
    


# @login_required
# def list_payment_methods(request):
#     try:
#         customer_id = request.user.credits.stripe_customer_id

#         payment_methods = stripe.PaymentMethod.list(
#             customer=customer_id,
#             type="card"
#         )

#         customer = stripe.Customer.retrieve(customer_id)
#         default_pm = customer.invoice_settings.default_payment_method

#         methods = []

#         for pm in payment_methods.data:
#             methods.append({
#                 "id": pm.id,
#                 "brand": pm.card.brand,
#                 "last4": pm.card.last4,
#                 "exp_month": pm.card.exp_month,
#                 "exp_year": pm.card.exp_year,
#                 "is_default": pm.id == default_pm
#             })

#         return JsonResponse({"methods": methods})

#     except Exception as e:
#         return JsonResponse({"methods": [], "error": str(e)})