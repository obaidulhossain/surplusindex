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

def ManageAutomation(request):
    params = request.POST if request.method == "POST" else request.GET
    automation_id = params.get("automation_id")
    automation = Automation.objects.get(pk=automation_id)
    states = Coverage.objects.filter(active=True).order_by("state")
    context = {
        "automation":automation,
        "states":states,
    }
    return render(request,"Automation/manage_automations.html",context)

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
                automation.name = subscription.name
                automation.price_amount = subscription.amount
                automation.price_id = subscription.price_id
                automation.description = subscription.description
                automation.save()
                return JsonResponse({"success": True})
            except SubscriptionPlan.DoesNotExist:
                return JsonResponse({"error": "Subscription plan not found"}, status=404)       
    except Automation.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

@login_required
def update_automation_setting(request):
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")

    automation = Automation.objects.get(
        client=request.user,
        status=Automation.ACTIVE
    )

    if field in ["auto_renew", "renew_when_expired", "renew_when_limit"]:
        setattr(automation, field, value)
        automation.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


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

@login_required
def stop_automation(request):
    data = json.loads(request.body)
    subscription_id = data.get("subscription_id")

    try:
        # Cancel Stripe subscription
        stripe.Subscription.delete(subscription_id)

        automation = Automation.objects.get(
            client=request.user,
            enrolled_stripe_subscrption=subscription_id
        )

        automation.status = Automation.PENDING
        automation.payment_status = Automation.FAILED
        automation.auto_renew = False
        automation.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
