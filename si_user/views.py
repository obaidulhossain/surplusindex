from django.shortcuts import render, redirect, get_object_or_404
from . forms import CreateUserForm, LoginForm, UpdateUserForm, UserDetailForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . models import *
# - authentication models and functions
from django.contrib.auth.models import auth
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
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
# Configure the logger

logging.basicConfig(level=logging.INFO)

stripe.api_key = settings.STRIPE_SECRET_KEY


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
    transactions = UserPayment.objects.filter(user=user_instance)
    credit_usage = CreditUsage.objects.filter(user=user_instance)
    user_credits = request.user.credits
    user_credits.update_total_credits()
    context = {
        'transactions':transactions,
        'credit_usage':credit_usage,
    }
    return render(request, 'si_user/user_profile.html', context)


@csrf_exempt
def userSubscription(request):
    session_id = request.GET.get('session_id', None)
    if session_id:

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                messages.success(request, "Payment Successful! Credits have been added to your purchased balance")
            else:
                messages.error(request,"Payment Failed. Please Try again.")

        except Exception as e:
            messages.error(request, "An error occured while verifying payment, Please try again.")

    return render(request, 'si_user/subscription.html')


# @login_required
# @csrf_exempt
logger = logging.getLogger(__name__)
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
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': priceID,  # Use dynamic price_id here
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('subscriptions')) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(reverse('subscriptions')),
                    customer=user.credits.stripe_customer_id,
                    client_reference_id=user.id,
                )
            except stripe.error.StripeError as e:
                logger.error(f"Error creating Stripe checkout session: {e}")
                return JsonResponse({'error': 'Failed to create Stripe checkout session.'}, status=400)
            try:
                return JsonResponse({
                    'session_id': session.id,
                    'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
                })
            except Exception as e:
                logger.error(f"Error creating JSON response: {e}")
                return JsonResponse({'error': 'Failed to create JSON response.'}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)



@csrf_exempt
def stripe_webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse("Invalid signature", status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        try:
            line_items = stripe.checkout.Session.list_line_items(session['id'])
            if not line_items['data']:
                return HttpResponse("No line items found", status=400)

            price_id = line_items['data'][0]['price']['id']
            price_map = {
                os.getenv('TEN_LEADS'): 10,
                os.getenv('FIFTY_LEADS'): 50,
                os.getenv('HUNDRED_LEADS'): 100,
                os.getenv('THREEHUNDRED_LEADS'): 300
            }
            num_leads = price_map.get(price_id, 0)

            customer_id = session.get('customer')
            checkout_id = session.get('id')
            amount_total = session.get('amount_total')
            if amount_total is None:
                return HttpResponse("Invalid session data", status=400)
            amount_paid = amount_total / 100
            currency = session.get('currency')
            user_id = session.get('client_reference_id')

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponse("User not found", status=404)

            with transaction.atomic():
                UserPayment.objects.create(
                    user=user,
                    stripe_customer_id=customer_id,
                    stripe_checkout_id=checkout_id,
                    amount=amount_paid,
                    number_of_leads=num_leads,
                    currency=currency,
                    has_paid=True,
                )
                user_detail = get_object_or_404(UserDetail, user=user)
                user_detail.purchased_credit_balance += num_leads
                user_detail.update_total_credits()
                user_detail.save()
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            return HttpResponse("Error processing webhook", status=400)

    else:
        logger.info(f"Unhandled event type: {event['type']}")
    return HttpResponse(status=200)





# @csrf_exempt
# def stripe_webhook(request):
#     # stripe.api_key = settings.STRIPE_SECRET_KEY
#     # You can find your endpoint's secret in your webhook settings
#     endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT
 
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE'] #.get and ,'' is added by cgpt
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
        
#         #Invalid Payload
#         return HttpResponse("Invalid Payload", status=400)
#     except stripe.error.SignatureVerificationError as e:
        
#         #Invalid Signature
#         return HttpResponse("Invalid Signature", status=400)
#     #Handle the checkout.session.completed event
#     if event['type'] == 'payment_intent.succeeded':
#         session = event['data']['object']
#         try:
#             # Fetch the line items using Stripe API
#             line_items = stripe.checkout.Session.list_line_items(session['id'])
#             price_id = line_items['data'][0]['price']['id']

#             # Determine the number of leads based on the price ID
#             if price_id == 'price_1QojYpG4c6thWCjhaNxkWBYH':  # Example price ID
#                 num_leads = 10
#             elif price_id == 'price_1QojZ9G4c6thWCjh9Ye4cxI9':
#                 num_leads = 50
#             elif price_id == 'price_1QoOCJG4c6thWCjhpEhUuWtH':
#                 num_leads = 100
#             elif price_id == 'price_1QojZNG4c6thWCjh4c4ljD2U':
#                 num_leads = 300
#             else:
#                 num_leads = 0
#                     # Extract other session data
#             customer_id = session.get('customer')
#             checkout_id = session.get('id')
#             amount_paid = session.get('amount_total') / 100  # Stripe uses cents
#             currency = session.get('currency')
#             user_id = session.get('client_reference_id')


#             user = User.objects.get(id=user_id)

#             with transaction.atomic():
#                 UserPayment.objects.create(
#                     user=user,
#                     stripe_customer_id=customer_id,
#                     stripe_checkout_id=checkout_id,
#                     amount=amount_paid,
#                     number_of_leads=num_leads,
#                     currency=currency,
#                     has_paid=True,
#                 )
#                 user_detail = get_object_or_404(UserDetail, user=user)
#                 user_detail.purchased_credit_balance += num_leads
#                 user_detail.update_total_credits()
#                 user_detail.save()

#         except Exception as e:
          
#             return HttpResponse("Error processing webhook", status=400)


#     return HttpResponse(status=200)







from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.credits.save()