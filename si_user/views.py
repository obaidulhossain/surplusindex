from django.shortcuts import render, redirect, get_object_or_404
import stripe.webhook
from . forms import CreateUserForm, LoginForm, UpdateUserForm, UserDetailForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . models import UserDetail, UserPayment
# - authentication models and functions
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
#stripe settings
import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


# -- subscription view --
# @login_required(login_url="login")
# def userSubscription(request):
#     if request.user.is_authenticated:
#         return render(request, 'si_user/subscription.html')
#     else:
#         messages.error(request, "Must be logged in to update subscription settings!")
#         return redirect('login')


# -- end of subscription view --

# -- Update User --

# -- End of Update User functi on --

    
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
def userSettings(request):
    current_user = request.user
    if UserDetail.objects.filter(user=current_user).exists():
        current_user_detail = get_object_or_404(UserDetail,user=current_user)
        user_form = UpdateUserForm(instance=current_user)
        detail_form = UserDetailForm(instance=current_user_detail)
        context = {
            'user_form':user_form,
            'detail_form':detail_form,
        }
        return render(request, 'si_user/user_settings.html', context)
    else:
        UserDetail.objects.create(user=current_user)
        return redirect('settings')

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
    user_credits = request.user.credits
    user_credits.update_total_credits()
    context = {

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


@login_required
@csrf_exempt
def checkout(request):
    user = request.user

    if not request.user.credits.stripe_customer_id:
        try:
            # Create a Stripe customer
            customer = stripe.Customer.create(
                email=request.user.email,
                name=f"{request.user.first_name} {request.user.last_name}",
            )
            request.user.credits.stripe_customer_id = customer.id
            request.user.credits.save()
        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            return JsonResponse({'error': str(e)}, status=400)

    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price' : 'price_1QoOCJG4c6thWCjhpEhUuWtH',
        'quantity' : 1,
    }],
    mode = 'payment',
    success_url = request.build_absolute_uri(reverse('subscriptions')) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url = request.build_absolute_uri(reverse('subscriptions')),
    customer=user.credits.stripe_customer_id,  # Link the customer ID
    client_reference_id=user.id,
    )

    return JsonResponse({
        'session_id':session.id,
        'stripe_public_key':settings.STRIPE_PUBLISHABLE_KEY,
    })
    


@csrf_exempt
def stripe_webhook(request):
    import os #cgpt code
    import logging #cgpt code
    logger = logging.getLogger(__name__) #cgpt code
    # You can find your endpoint's secret in your webhook settings
    endpoint_secret = 'whsec_03c33e2abac5493e1a5f30ae7f72a9be6e34bd155db08d6febaf67936e5bfcb8'
 
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE','') #.get and ,'' is added by cgpt
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error("Invalid Payload", exc_info=e) #cgpt code
        #Invalid Payload
        return HttpResponse("Invalid Payload", status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid Signature", exc_info=e)
        #Invalid Signature
        return HttpResponse("Invalid Signature", status=400)
    #Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # print(json.dumps(session,indent=4))
        
        customer_id = session.get('customer')
        checkout_id = session.get('id')
        amount_paid = session.get('amount_total') / 100  # Stripe uses cents
        currency = session.get('currency')
        user_id = session.get('client_reference_id')  # Pass this in the checkout creation
        num_leads = 100  # This could vary depending on your logic

        try:
            user = User.objects.get(id=user_id)
            UserPayment.objects.create(
                user=user,
                stripe_customer_id=customer_id,
                stripe_checkout_id=checkout_id,
                amount=amount_paid,
                number_of_leads=num_leads,
                currency=currency,
                has_paid=True,
            )
            update_user_detail = get_object_or_404(UserDetail,user=user)
            update_user_detail.purchased_credit_balance += num_leads
            update_user_detail.update_total_credits()
            # update_user_detail.save()

            logger.info(f"Payment successfully recorded for user {user.username}")
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist.")
            return HttpResponse("User does not exist", status=400)
    
    return HttpResponse(status=200)


from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.credits.save()