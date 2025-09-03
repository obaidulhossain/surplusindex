from django.shortcuts import render, redirect, get_object_or_404
from . forms import CreateUserForm, LoginForm, UpdateUserForm, UserDetailForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . models import *
from AllSettings.models import *
# - authentication models and functions
from django.contrib.auth.models import auth
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.urls import reverse
#stripe settings
import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import logging #cgpt code
import os
from django.utils.timezone import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta, date
from collections import defaultdict
# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


## test if api key is working
# try:
#     stripe.Product.list(limit=1)  # Fetch a product to test the connection
#     print("API key is okay")
# except stripe.error.AuthenticationError:
#     print("Invalid Stripe API key.")
## end test if api key is working

@login_required(login_url="login")
def userSettings(request):
    current_user = request.user
    user_instance = User.objects.get(username=current_user)
    if UserDetail.objects.filter(user=current_user).exists():
        current_user_detail = get_object_or_404(UserDetail,user=current_user)
        user_form = UpdateUserForm(instance=current_user)
        detail_form = UserDetailForm(instance=current_user_detail)
        password_form = PasswordChangeForm(request.user)
        context = {
            'user_form':user_form,
            'detail_form':detail_form,
            'password_form':password_form,
            'user_instance':user_instance,
        }
        return render(request, 'si_user/user_settings.html', context)
    else:
        UserDetail.objects.create(user=current_user)
        return redirect('settings')

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'user_form': UpdateUserForm(instance=request.user),
                'detail_form': UserDetailForm(instance=request.user.userdetail) if hasattr(request.user, 'userdetail') else None,
                'password_form': form,
            }
            return render(request, 'si_user/user_settings.html', context)
    else:
        return redirect('settings')

# ------------------------------------- Login View
def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
    context = {'loginform':form}
    
    return render(request, 'login.html', context=context)

# ------------------------------------- Logout View  

# ------------------------------------- Register View
def register (request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("my-login")
    context = {'registerform':form}
    return render(request, 'register.html', context=context)

# ------------------------------------- Dashboard View
@login_required(login_url="my-login")
def dashboard(request):
    
    return render(request, 'dashboard.html')

@login_required(login_url="login")
def updateUserCredentials(request):
    current_user = request.user
    current_user_detail = get_object_or_404(UserDetail,user=current_user)
    if request.method == 'POST':

        user_form =UpdateUserForm(request.POST, instance=current_user)
        detail_form = UserDetailForm(request.POST, instance=current_user_detail)
        if user_form.is_valid() and detail_form.is_valid():
            user_form.save()
            detail_form.save()

            messages.success(request, "User Has Been Updated Successfully!")
            return redirect('settings')
        else:
            user_form = UpdateUserForm(instance=current_user)
            detail_form = UserDetailForm(instance=current_user_detail)
            messages.error(request, "Invalid Credentials")

@login_required(login_url="login")
def userProfile(request):
    user = request.user
    user_instance = User.objects.get(username=user)
    transactions = UserTransactions.objects.filter(user=user_instance)
    subscriptions = StripeSubscription.objects.filter(user=user_instance, status='active').order_by('-created_at')
    credit_usage = CreditUsage.objects.filter(user=user_instance)
    user_credits = request.user.credits
    user_credits.update_total_credits()
    context = {
        'transactions':transactions,
        'subscriptions':subscriptions,
        'credit_usage':credit_usage,
    }
    return render(request, 'si_user/user_profile.html', context)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.credits.save()



@csrf_exempt
def userSubscription(request):
    user = request.user
    UserSettings, created = ClientSettings.objects.get_or_create(
        user=user,
        defaults={'manage_sub_show_hidden': False}
        )
    
    Plans = SubscriptionPlan.objects.filter(active=True).order_by('name').exclude(type="payperlead")
    payperlead_options = SubscriptionPlan.objects.filter(type="payperlead", active=True).order_by('amount')
    subscriptions = StripeSubscription.objects.filter(user=user).order_by('current_period_end')
    if not UserSettings.manage_sub_show_hidden:
        subscriptions = subscriptions.exclude(hidden=True)
    # Get all transactions for this user in one query
    transactions = UserTransactions.objects.filter(user=user).order_by('-created_at')
    announcements = Announcements.objects.filter(effective_date__gte=date.today(), published=True).order_by('created_at')
    # Group transactions by subscription ID
    transactions_map = defaultdict(list)
    for tx in transactions:
        transactions_map[tx.stripe_subscription_id].append(tx)

    # Attach transactions to each subscription
    for subs in subscriptions:
        subs.transactions = transactions_map.get(subs.subscription_id, [])

    session_id = request.GET.get('session_id', None)
    if session_id:

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                messages.success(request, "Payment Successful! Credits / Subscription Updated")
            else:
                messages.error(request,"Payment Failed. Please Try again.")

        except Exception as e:
            messages.error(request, "An error occured while verifying payment, Please try again.")
    context = {
        'Plans':Plans,
        'payperlead_options':payperlead_options,
        'subscriptions':subscriptions,
        'UserSettings':UserSettings,
        'announcements':announcements,
    }
    return render(request, 'si_user/subscription.html', context)

def HideShow_HiddenSubs(request):
    if request.method == "POST":
        ShowHidden = request.POST.get('show_hide_hidden')
        settings = ClientSettings.objects.get(user=request.user)
        if ShowHidden == 'on':
            settings.manage_sub_show_hidden = True
        else:
            settings.manage_sub_show_hidden = False
        settings.save()
    return redirect('subscriptions')



@login_required
@csrf_exempt
def checkout(request):
    user = request.user
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            priceID = data.get('price_id')
            leads = data.get('leads')
            amount = data.get('amount')
            if not priceID or leads is None or amount is None:
                    return JsonResponse({'error': 'price_id, leads, or amount are missing'}, status=400)
            if not user.credits.stripe_customer_id:
                try:
                    customer = stripe.Customer.create(
                        email=user.email,
                        name=f"{user.first_name} {user.last_name}",
                    )
                    user.credits.stripe_customer_id = customer.id
                    user.credits.save()
                except stripe.error.StripeError as e:
                    return JsonResponse({'error': 'Failed to create Stripe customer.'}, status=400)
            
            # Check if priceID belongs to a subscription plan or payperlead
            try:
                plan = SubscriptionPlan.objects.get(price_id=priceID, active=True)
            except SubscriptionPlan.DoesNotExist:
                return JsonResponse({'error': 'Invalid price_id'}, status=400)
   
            # Determine Stripe Checkout mode
            if plan.type == 'subscription':
                mode = 'subscription'
            else:
                mode = 'payment'

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': priceID,  # Use dynamic price_id here
                        'quantity': 1,
                    }],
                    mode=mode,
                    success_url=request.build_absolute_uri(reverse('subscriptions')) + '?session_id={CHECKOUT_SESSION_ID}',
                    
                    cancel_url=request.build_absolute_uri(reverse('subscriptions')),
                    customer=user.credits.stripe_customer_id,
                    client_reference_id=user.id,
                )
            except stripe.error.StripeError as e:
                return JsonResponse({'error': 'Failed to create Stripe checkout session.'}, status=400)
            try:
                return JsonResponse({
                    'session_id': session.id,
                    'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
                })
            except Exception as e:
                return JsonResponse({'error': 'Failed to create JSON response.'}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

User = get_user_model()

@csrf_exempt
def stripe_webhook(request):
    logger.info("⚡ Stripe webhook triggered")
    endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT

    if request.content_type != "application/json":
        logger.warning("Invalid content type on webhook request")
        return HttpResponse("Invalid content type", status=400)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.error("Invalid payload in Stripe webhook")
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe signature")
        return HttpResponse("Invalid signature", status=400)

    event_type = event.get("type")
    data_object = event["data"]["object"]
    logger.info(f"Received Stripe event: {event_type}")

    # --- Helpers ---
    def create_or_update_transaction(user, amount, currency, status, source_type, stripe_ids, num_leads=0):
        """
        Create or update a subscription or PAYG transaction.
        """
        with transaction.atomic():
            if source_type == "subscription" and stripe_ids.get("subscription_id"):
                try:
                    payment = UserTransactions.objects.get(stripe_subscription_id=stripe_ids.get("subscription_id"))
                    # Update fields only if provided
                    payment.user = user
                    payment.stripe_customer_id = stripe_ids.get("customer") or payment.stripe_customer_id
                    payment.stripe_checkout_id = stripe_ids.get("checkout_id") or payment.stripe_checkout_id
                    payment.stripe_invoice_id = stripe_ids.get("invoice_id") or payment.stripe_invoice_id
                    payment.amount = amount
                    payment.currency = currency
                    payment.number_of_leads = num_leads
                    payment.status = status
                    payment.transaction_source = source_type
                    payment.has_paid = (status == "active")
                    payment.save()
                    logger.info(f"Subscription transaction updated for {user.username}")
                except UserTransactions.DoesNotExist:
                    payment = UserTransactions.objects.create(
                        user=user,
                        stripe_customer_id=stripe_ids.get("customer"),
                        stripe_checkout_id=stripe_ids.get("checkout_id"),
                        stripe_subscription_id=stripe_ids.get("subscription_id"),
                        stripe_invoice_id=stripe_ids.get("invoice_id"),
                        amount=amount,
                        currency=currency,
                        number_of_leads=num_leads,
                        status=status,
                        transaction_source=source_type,
                        has_paid=(status == "active")
                    )
                    logger.info(f"Subscription transaction created for {user.username}")
                return payment
            else:
                # PAYG or normal create
                payment = UserTransactions.objects.create(
                    user=user,
                    stripe_customer_id=stripe_ids.get("customer"),
                    stripe_checkout_id=stripe_ids.get("checkout_id"),
                    stripe_subscription_id=stripe_ids.get("subscription_id"),
                    stripe_invoice_id=stripe_ids.get("invoice_id"),
                    amount=amount,
                    currency=currency,
                    number_of_leads=num_leads,
                    status=status,
                    transaction_source=source_type,
                    has_paid=(status == "active")
                )
                logger.info(f"PAYG transaction created for {user.username}")
                return payment
            
            
    def update_subscription(subscription_id, status=None, period_end=None):
        try:
            sub = StripeSubscription.objects.get(subscription_id=subscription_id)
            if status:
                sub.status = status
            if period_end:
                sub.current_period_end = period_end
            sub.save()
            logger.info(f"Subscription {subscription_id} updated for {sub.user.username}")
        except StripeSubscription.DoesNotExist:
            logger.warning(f"Subscription {subscription_id} not found in DB")

    # --- Event Handlers ---
    if event_type == "checkout.session.completed":
        session = data_object
        user_id = session.get("client_reference_id")
        if not user_id:
            logger.error("checkout.session.completed missing client_reference_id")
            return HttpResponse("No user reference", status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            return HttpResponse("User not found", status=404)

        # Fetch line items to identify the plan
        try:
            line_items = stripe.checkout.Session.list_line_items(session["id"])
            if not line_items["data"]:
                logger.error("No line items found in checkout session")
                return HttpResponse("No line items found", status=400)
            price_id = line_items["data"][0]["price"]["id"]
        except Exception as e:
            logger.exception(f"Error fetching line items: {e}")
            return HttpResponse("Error fetching line items", status=400)

        amount_paid = session.get("amount_total", 0) / 100
        currency = session.get("currency")
        plan = SubscriptionPlan.objects.filter(price_id=price_id, active=True).first()

        if plan and plan.type == "subscription":
            subscription_id = session.get("subscription")
            stripe_sub_data = stripe.Subscription.retrieve(subscription_id)
            current_period_end = datetime.fromtimestamp(stripe_sub_data.current_period_end)

            StripeSubscription.objects.update_or_create(
                user=user,
                subscription_id=subscription_id,
                defaults={
                    "plan": plan,
                    "customer_id": session.get("customer"),
                    "status": "active",
                    "current_period_end": current_period_end,
                }
            )

            create_or_update_transaction(
                user=user,
                amount=amount_paid,
                currency=currency,
                status="active",
                source_type="subscription",
                stripe_ids={
                    "customer": session.get("customer"),
                    "checkout_id": session.get("id"),
                    "subscription_id": subscription_id,
                    "invoice_id": None
                }
            )

        else:
            # Pay-as-you-go mapping
            # price_map = {
            #     os.getenv("TEN_LEADS"): 10,
            #     os.getenv("FIFTY_LEADS"): 50,
            #     os.getenv("HUNDRED_LEADS"): 100,
            #     os.getenv("THREEHUNDRED_LEADS"): 300
            # }
            # num_leads = price_map.get(price_id, 0)
            sub_instance = SubscriptionPlan.objects.get(price_id=price_id)
            num_leads = int(sub_instance.lead_number)
            
            with transaction.atomic():
                create_or_update_transaction(
                    user=user,
                    amount=amount_paid,
                    currency=currency,
                    status="active",
                    source_type="payg",
                    stripe_ids={
                        "customer": session.get("customer"),
                        "checkout_id": session.get("id"),
                        "subscription_id": None,
                        "invoice_id": None
                    },
                    num_leads=num_leads
                )
                user_detail = get_object_or_404(UserDetail, user=user)
                user_detail.purchased_credit_balance += num_leads
                user_detail.update_total_credits()
                user_detail.save()
                logger.info(f"Updated credits for {user.username} (+{num_leads} leads)")

    elif event_type in ("invoice.payment_succeeded", "invoice.paid", "invoice.payment_failed"):
        invoice_id = data_object["id"]
        invoice = stripe.Invoice.retrieve(invoice_id, expand=["lines.data"])
        subscription_id = invoice.get("subscription")
        amount_paid = invoice.get("amount_paid", 0) / 100
        currency = invoice.get("currency")
        status = "active" if event_type != "invoice.payment_failed" else "failed"

        period_end = None
        try:
            lines = invoice.get("lines", {}).get("data", [])
            if lines and "period" in lines[0]:
                period_end = datetime.fromtimestamp(lines[0]["period"]["end"])
        except Exception as e:
            logger.warning(f"Could not parse period_end for {subscription_id}: {e}")

        update_subscription(subscription_id, status=status, period_end=period_end)

        try:
            sub = StripeSubscription.objects.get(subscription_id=subscription_id)
            user = sub.user
        except StripeSubscription.DoesNotExist:
            logger.warning(f"Subscription {subscription_id} not found for invoice {invoice.get('id')}")
            user = None

        if user:
            txn = create_or_update_transaction(
                user=user,
                amount=amount_paid,
                currency=currency,
                status=status,
                source_type="subscription",
                stripe_ids={
                    "customer": invoice.get("customer"),
                    "checkout_id": None,
                    "subscription_id": subscription_id,
                    "invoice_id": invoice.get("id")
                }
            )
            if status == "active":
                txn.mark_as_paid()
            else:
                txn.mark_as_failed()
        else:
            # fallback log/creation to avoid losing data
            logger.error(f"Missing subscription {subscription_id}, could not attach invoice {invoice['id']} to user")
    elif event_type == "customer.subscription.updated":
        sub_data = data_object
        period_end = datetime.fromtimestamp(sub_data["current_period_end"]) if sub_data.get("current_period_end") else None
        update_subscription(sub_data.get("id"), status=sub_data.get("status"), period_end=period_end)

    elif event_type == "customer.subscription.deleted":
        sub_data = data_object
        update_subscription(sub_data.get("id"), status="canceled")

    else:
        logger.info(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)

@login_required
def cancel_subscription(request, subscription_id):
    # sub = get_object_or_404(
    #     StripeSubscription,
    #     user=request.user,
    #     subscription_id=subscription_id,
    #     status="active"
    # )
    stripe.Subscription.delete(subscription_id)  # Immediate cancel
    messages.success(request, f"Subscription {subscription_id} has been canceled.")
    return redirect("subscriptions")
# def cancel_subscription(request):
#     sub = get_object_or_404(StripeSubscription, user=request.user, status="active")
#     stripe.Subscription.delete(sub.subscription_id)  # immediate cancel
#     messages.success(request, "Your subscription has been canceled.")
#     return redirect("subscription_settings")

@login_required
def pause_subscription(request):
    sub = get_object_or_404(StripeSubscription, user=request.user, status="active")
    stripe.Subscription.modify(sub.subscription_id, pause_collection={'behavior': 'mark_uncollectible'})
    messages.success(request, "Your subscription has been paused.")
    return redirect("subscription_settings")

@login_required
def resume_subscription(request):
    sub = get_object_or_404(StripeSubscription, user=request.user, status="paused")
    stripe.Subscription.modify(sub.subscription_id, pause_collection="")
    messages.success(request, "Your subscription has been resumed.")
    return redirect("subscription_settings")

@login_required
def extend_subscription(request):
    sub = get_object_or_404(StripeSubscription, user=request.user, status="active")
    new_period_end = int((datetime.utcnow() + timedelta(days=30)).timestamp())
    stripe.Subscription.modify(sub.subscription_id, trial_end=new_period_end)
    messages.success(request, "Your subscription validity has been extended by 30 days.")
    return redirect("subscription_settings")

from django.views.decorators.http import require_POST
@require_POST
@login_required
def hide_show_subscription(request):
    if request.method == "POST":
        sub_id = request.POST.get('sub_id')
        sub = get_object_or_404(StripeSubscription, id=sub_id, user=request.user)
        sub.hidden = not sub.hidden
        sub.save()
        messages.info(request, f"{sub.plan.name} Plan marked as {'Hidden' if sub.hidden else 'Unhidden'}")
    return redirect("subscriptions")



