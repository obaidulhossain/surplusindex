from django.contrib import messages, auth
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User, auth, Group
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse, HttpResponse
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from django.views import View
from validate_email import validate_email

import json

from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from .utils import token_generator
from django.contrib.sites.shortcuts import get_current_site
from si_user.models import UserDetail
from Communication.utils import notify
stripe.api_key = settings.STRIPE_SECRET_KEY


# Shows the homepage surplusindex.com ----------
def homepage(request):
    return render(request, 'index.html')

@csrf_exempt
def ValidateUsername(request):
    data=json.loads(request.body)
    username=data['username']

    if not str(username).isalnum():
            return JsonResponse({'username_error':'Only alphanumeric characters are allowed.'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'username_error':'Username exists, try another.'}, status=409)
    return JsonResponse({'username_valid': True})

@csrf_exempt
def ValidateEmail(request):
    data = json.loads(request.body)
    email = data['email']
    if not validate_email(email):
        return JsonResponse({'email_error':'Invalid email.'}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({'email_error':'Email already in use, try another.'}, status=409)        
    return JsonResponse({'email_valid': True})

# class UsernameValidationView(View):
#     def post(self, request):
#         data=json.loads(request.body)
#         username=data['username']

#         if not str(username).isalnum():
#             return JsonResponse({'username_error':'Only alphanumeric characters are allowed.'}, status=400)
#         if User.objects.filter(username=username).exists():
#             return JsonResponse({'username_error':'Username exists, try another.'}, status=409)
#         return JsonResponse({'username_valid': True})


# validates email while registering ------------
# class EmailValidationView(View):
#     def post(self, request):
#         data = json.loads(request.body)
#         email = data['email']
#         if not validate_email(email):
#             return JsonResponse({'email_error':'Invalid email'}, status=400)
#         if User.objects.filter(email=email).exists():
#             return JsonResponse({'email_error':'Email already in use, please provide another'}, status=409)        
#         return JsonResponse({'email_valid': True})




class VerificationView(View):
    def get(self, request, uidb64, token):
        
        
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect ('login'+'?message='+'User already activated')
            

            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()
            update_detail = UserDetail.objects.get(user=user)
            update_detail.update_total_credits()
            notify(
                    n_subject="New Activation",
                    n_body=f"A new user registered with username {user.username} and email {user.email} activated his/her account successfully!",
                    n_source="Activation")
            messages.success(request,'Account Successfully Activated')
            return redirect ('homepage')
        except Exception as ex:
            pass
        
        

        return redirect('homepage')
    
def Register(request):
    context = {
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
        }
    return render(request, 'authentication/registration.html',context)

@csrf_exempt
def start_registration(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        # Store temporarily in session
        request.session["registration_data"] = {
            "username": username,

            "email": email,
            "password": password,
        }

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=username,
        )
        request.session["stripe_customer_id"] = customer.id

        # Create SetupIntent
        setup_intent = stripe.SetupIntent.create(
            customer=customer.id,
            payment_method_types=["card"],
        )

        return JsonResponse({
            "clientSecret": setup_intent.client_secret
        })

@csrf_exempt
def complete_registration(request):
    if request.method == "POST":
        # data = json.loads(request.body)
        registration_data = request.session.get("registration_data")      
        customer_id = request.session.get("stripe_customer_id")

        # email = data.get("email")
        # username = data.get("username")
        # password = data.get("password")
        # customer_id = data.get("customerId")
        if not registration_data or not customer_id:
            return JsonResponse({"error": "Session expired"}, status=400)
        # Create Django user
        user = User.objects.create_user(
            username=registration_data["username"],
            email=registration_data["email"],
            password=registration_data["password"],
        )
        user.is_active=True
        user.groups.add(Group.objects.get(name='clients'))
        user.save()
        # Save Stripe customer ID
        user.credits.stripe_customer_id = customer_id
        user.credits.save()
        # Clear session temp data
        del request.session["registration_data"]
        del request.session["stripe_customer_id"]
        login(request, user)

        return JsonResponse({"status": "success"})

#---------------------------------Login Start

def Login(request):
    return render(request,'authentication/login.html')

def LoginAuthenticate(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        if username_or_email and password:
            if "@" in username_or_email:
                user_ins = User.objects.filter(email=username_or_email).first()
                if user_ins:
                    username = user_ins.username
                else:
                    username = username_or_email
            else:
                username = username_or_email
            
            
            user = User.objects.filter(username=username).first()
            if user:
                if user.is_active:
                    active_user=auth.authenticate(username=username,password=password)
                    if active_user:
                        auth.login(request, active_user)
                        messages.success(request, 'Welcome back!')
                        return redirect('dashboard')
                        
                    else:
                            
                        messages.error(request,'Invalid Credentials')
                        return redirect('homepage')
                else:
                    if user.check_password(password):
                        detail = getattr(user, 'credits', None)
                        if detail and detail.activation_attempt >= 10:
                            return JsonResponse({'success': False, 'error': 'Maximum Activation Attempt reached, Please <a href="mailto:contact@surplusindex.com">contact</a>'})
                        else:
                            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                            domain = get_current_site(request).domain
                            link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                            activate_url = f"http://{domain}{link}"

                            # send mail
                            send_mail(
                                "Activate SurplusIndex Account",
                                f"Hi {user.username},\n\nYour SurplusIndex account is created successfully!\n\nPlease use this link to activate your account and get access to thousands of up to date surplus leads:\n{activate_url}\n\n\n\n Note that: Inactive user accounts will be deleted after 3rd activation remainder.",
                                "contact@surplusindex.com",
                                [user.email],
                                fail_silently=False
                            )

                            # increment attempts
                            if detail:
                                detail.activation_attempt += 1
                                detail.save()
                        messages.error(request, 'Activation token sent, please check your email')
                        return redirect('homepage')
                    else:
                        messages.error(request,'Invalid Credentials')
                        return redirect('homepage')
            messages.error(request,'Invalid Credentials')
            return redirect('homepage')
        messages.error(request,'Please fill out all the fields')
        return redirect('homepage')

#---------------------------------Login End



@login_required(login_url="login")
def user_logout(request):
    auth.logout(request)
    return redirect("homepage")





# class RegistrationView(View):
#     def get(self, request):
#         context = {
#                 "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
#             }
#         return render(request, 'authentication/registration.html',context)
    
#     def post(self, request):
#         #GET USER DATA
#         #VALIDATE
#         #CREATE USER ACCOUNT

#         username=request.POST['username']
#         email=request.POST['email']
#         password=request.POST['password']

#         context={
#             'fieldValues':request.POST

#         }

#         if not User.objects.filter(username=username).exists():
#             if not User.objects.filter(email=email).exists():
#                 if len(password)<6:
#                     messages.error(request,'Password too short')
#                     return render(request, 'authentication/registration.html', context)
#                 user = User.objects.create_user(username=username, email=email)
#                 user.set_password(password)
#                 user.is_active=False
#                 user.groups.add(Group.objects.get(name='clients'))
#                 user.save()

#                 #activation token
#                 uidb64=urlsafe_base64_encode(force_bytes(user.pk))
#                 domain = get_current_site(request).domain
#                 link = reverse('activate',kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})
#                 activate_url='http://'+domain+link
                
#                 email_body='Hi '+user.username+' Please use this link to verify your email and activate your account.\n'+activate_url
#                 email_subject = 'Verify Email and Activate SurplusIndex Account'
#                 send_mail(email_subject,email_body,'contact@surplusindex.com',[email], fail_silently=False)
                
#                 notify(
#                     n_subject="New Registration",
#                     n_body=f"A new user registered with username {username} and email {email} (Not Activated)",
#                     n_source="Registration")
#                 messages.success(request,'Account Successfully Created')
#                 messages.info(request, 'Account Inactive! Please Check your email to activate account')
#                 return redirect('homepage')
#             context = {
#                 "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
#             }

#         return render(request, 'authentication/registration.html', context)
    


# class LoginView(View):
#     def get(self,request):
#         return render(request,'authentication/login.html')
     
#     def post(self, request):
#         username_or_email = request.POST['username']
#         password = request.POST['password']
    
#         if username_or_email and password:
#             if "@" in username_or_email:
#                 user_ins = User.objects.filter(email=username_or_email).first()
#                 if user_ins:
#                     username = user_ins.username
#                 else:
#                     username = username_or_email
#             else:
#                 username = username_or_email
#             user=auth.authenticate(username=username,password=password)

#             if user: 
#                 if user.is_active:
#                     auth.login(request, user)
#                     messages.success(request, 'Welcome, '+user.username+' you are now logged in')
#                     return redirect('dashboard')
#                 messages.error(request,'Account is not active, please check your email to activate account')
#                 return render(request,'authentication/login.html')
#             messages.error(request,'Invalid Credentials')
#             return render(request,'authentication/login.html')
#         messages.error(request,'Please fill out all the fields')
#         return render(request,'authentication/login.html')