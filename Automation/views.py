from django.shortcuts import render, redirect
from .models import*
import stripe
import json
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from AllSettings.models import Coverage
from django.views.decorators.csrf import csrf_exempt
from authentication.decorators import card_required
from .services.stripe_subscription_service import StripeSubscriptionService
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users
from django.db.models import Exists, OuterRef
from ProjectManager.resources import DashboardCloneExportResource
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from .resources import CustomExportResource
stripe.api_key = settings.STRIPE_SECRET_KEY

@allowed_users(['admin'])
@login_required(login_url="login")
def AdminAutomation(request):
    automations_active = Automation.objects.filter(status=Automation.ACTIVE)
    context = {
        "automations_active":automations_active,
    }
    return render(request, "Automation/admin_automation.html",context)


def AdminManageAutomation(request):
    params = request.POST if request.method == "POST" else request.GET
    automation_id = params.get("automation_id")
    automation = Automation.objects.get(pk=automation_id)
    states = Coverage.objects.filter(active=True).order_by("state")
    user_detail = UserDetail.objects.get(user=automation.client)
    sale_type = []
    if automation.tax:
        sale_type.append(Foreclosure.TAX)
    if automation.mortgage:
        sale_type.append(Foreclosure.MORTGAGE)
    
    base_filters = {
        "published": True,
        "state__in": automation.states
    }
    if sale_type:
        base_filters["sale_type__in"] = sale_type
    

    pre_f_qs = (Foreclosure.objects
                .filter(**base_filters, sale_status=Foreclosure.ACTIVE)
                .exclude(pre_f_delivered=user_detail)
                .annotate(in_delivery=Exists(automation.pre_f_to_deliver.filter(id=OuterRef("id"))))
                )
    post_f_qs = (Foreclosure.objects
                 .filter(**base_filters, sale_status=Foreclosure.SOLD, surplus_status=Foreclosure.POSSIBLE_SURPLUS, possible_surplus__gte=automation.surplus_capped)
                 .exclude(post_f_delivered=user_detail)
                 .annotate(in_delivery=Exists(automation.post_f_to_deliver.filter(id=OuterRef("id"))))
                 )
    verified_s_qs = (Foreclosure.objects
                     .filter(**base_filters, sale_status=Foreclosure.SOLD, surplus_status=Foreclosure.FUND_AVAILABLE, verified_surplus__gte=automation.surplus_capped)
                     .exclude(verified_s_delivered=user_detail)
                     .annotate(in_delivery=Exists(automation.verified_s_to_deliver.filter(id=OuterRef("id"))))
                     )
    
    context = {
        "automation":automation,
        "states":states,
        "pre_f_qs":pre_f_qs,
        "post_f_qs":post_f_qs,
        "verified_s_qs":verified_s_qs,
    }
    return render(request,"Automation/admin_manage_automations.html",context)

@login_required
def toggle_post_delivery(request):

    if request.method == "POST":

        data = json.loads(request.body)

        foreclosure_id = data.get("foreclosure_id")
        checked = data.get("checked")
        automationId = data.get("automation_id")
        automation = Automation.objects.get(pk=automationId)

        foreclosure = Foreclosure.objects.get(id=foreclosure_id)

        if checked:
            automation.post_f_to_deliver.add(foreclosure)
        else:
            automation.post_f_to_deliver.remove(foreclosure)

        return JsonResponse({
            "success": True,
            "count": automation.post_f_to_deliver.count()
            })

@login_required
def toggle_verified_delivery(request):

    if request.method == "POST":

        data = json.loads(request.body)

        foreclosure_id = data.get("foreclosure_id")
        checked = data.get("checked")
        automationId = data.get("automation_id")
        automation = Automation.objects.get(pk=automationId)

        foreclosure = Foreclosure.objects.get(id=foreclosure_id)

        if checked:
            automation.verified_s_to_deliver.add(foreclosure)
        else:
            automation.verified_s_to_deliver.remove(foreclosure)

        return JsonResponse({
            "success": True,
            "count": automation.verified_s_to_deliver.count()
            })


@login_required(login_url="login")
@allowed_users(['admin'])
def download_automation_leads(request):
    # if request.method == "POST":
    # data = json.loads(request.body)
    # field = data.get("data_field")
    # atmID = data.get("automation_id")
    field = request.GET.get("data_field")
    atmID = request.GET.get("automation_id")
    automation = Automation.objects.get(pk=atmID)
    
        
    if field =="post_f":
        queryset = automation.post_f_to_deliver.all()
    elif field == "verified_s":
        queryset = automation.verified_s_to_deliver.all()
    elif field == "pre_f":
        queryset = automation.pre_f_to_deliver.all()
    else:
        queryset = None
        return JsonResponse({"error": "Field Name Not Matched!"}, status=400)
    if len(queryset) <1:
        return JsonResponse({"error": "Treshold is empty"}, status=400)
    
    resource = DashboardCloneExportResource(queryset)
    filename, buffer, _ = resource.export_to_excel("Automation Leads")

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response



@staff_member_required
def run_automation_delivery(request):
    if request.method == "POST":
        try:
            call_command("process_automation_delivery")
            return JsonResponse({"status": "success", "message": "Automation delivery executed."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



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
    transactions = automation.transaction.all()
    deliveries = AutomationDeliveries.objects.filter(automation=automation, client=automation.client)
    context = {
        "automation":automation,
        "states":states,
        "transactions":transactions,
        "deliveries":deliveries,

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
        print(f"sub id: {sub_id}")
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

def getPrices(request):
    planID = request.GET.get("plan_id")
    automation = Automation.objects.get(pk=planID)
    options = SubscriptionPlan.objects.filter(stripe_product_id = automation.subscription.stripe_product_id)
    installment_options = []
    no_installment_price_id = None
    planName = None
    planDescription = None
    if options.count() > 1:
        for price in options:
            installment_options.append({
                "id":price.pk,
                "price_id": price.price_id,
                "label": f"{price.name} - {price.amount}",
                "planName" : price.name,
                "planDescription" : price.amount,
            })
    else:
        no_installment_price_id = automation.price_id
        planName = automation.name
        planDescription = automation.price_amount
    return JsonResponse({
        "has_installments" : bool(installment_options),
        "options" : installment_options,
        "no_installment_price_id" : no_installment_price_id,
        "planName" : planName,
        "planDescription" : planDescription,
    })

def check_installments(request):
    price_id = request.GET.get("price_id")
    current_plan = SubscriptionPlan.objects.get(price_id = price_id)
    options = SubscriptionPlan.objects.filter(stripe_product_id = current_plan.stripe_product_id)
    print(options)
    installment_options = []
    if options.count() > 1:
        for price in options:
            installment_options.append({
                "price_id": price.price_id,
                "label": f"{price.name} - {price.amount}"
            })
    print(installment_options)        
    return JsonResponse({
        "has_installments": bool(installment_options),
        "options": installment_options
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

    if payment_intent.status in ["requires_action", "requires_confirmation"]:
        return JsonResponse({
            "requires_action": True,
            "client_secret": payment_intent.client_secret
        })
    elif payment_intent.status == "succeeded":
        return JsonResponse({"success": True})
    elif payment_intent.status == "requires_payment_method":
        error_message = None
        if payment_intent.last_payment_error:
            error_message = payment_intent.last_payment_error.get("message")
        return JsonResponse({
            "error": error_message or "Your card was declined."
        })

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
def download_invoice(request, invoice_id):

    try:
        invoice = stripe.Invoice.retrieve(invoice_id)

        return redirect(invoice.invoice_pdf)

    except stripe.error.StripeError:
        return HttpResponse("Invoice not found", status=404)

@login_required
def download_delivery_data(request, delivery_id):

    delivery = AutomationDeliveries.objects.select_related(
        "automation", "client"
    ).prefetch_related(
        "data__lead"
    ).get(id=delivery_id)

    # convert Status → Foreclosure
    queryset = [status.lead for status in delivery.data.all() if status.lead]

    if not queryset:
        return HttpResponse("No data found.", status=404)
    
    # reuse your existing export system
    resource = CustomExportResource(
        delivery.automation,
        queryset,
        delivery.get_list_type_display()
    )

    filename, buffer, df = resource.export_to_excel()

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response