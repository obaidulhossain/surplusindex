from django.contrib import messages, auth
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User, auth, Group
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail

from django.http import JsonResponse

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



# Shows the homepage surplusindex.com ----------
def homepage(request):
    return render(request, 'index.html')



# validates email while registering ------------
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'Invalid email'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Email already in use, please provide another'}, status=409)        
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username=data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry! Username already exists, please try another'}, status=409)        
        return JsonResponse({'username_valid': True})
      

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/registration.html')
    
    def post(self, request):
        #GET USER DATA
        #VALIDATE
        #CREATE USER ACCOUNT

        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        context={
            'fieldValues':request.POST

        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'Password too short')
                    return render(request, 'authentication/registration.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active=False
                user.groups.add(Group.objects.get(name='clients'))
                user.save()

                #activation token
                uidb64=urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate',kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})
                activate_url='http://'+domain+link
                
                email_body='Hi '+user.username+' Please use this link to verify your email and activate your account.\n'+activate_url
                email_subject = 'Verify Email and Activate SurplusIndex Account'
                send_mail(email_subject,email_body,'contact@surplusindex.com',[email], fail_silently=False)
                
                notify(
                    n_subject="New Registration",
                    n_body=f"A new user registered with username {username} and email {email} (Not Activated)",
                    n_source="Registration")
                messages.success(request,'Account Successfully Created')
                messages.info(request, 'Account Inactive! Please Check your email to activate account')
                return redirect('login')

        return render(request, 'authentication/registration.html')
    

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
            messages.info(request,'You have recieved 20 Free credits. Log in and access thousands of active prospects now.')
            return redirect ('login')
        except Exception as ex:
            pass
        
        

        return redirect('login')


class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')
     
    def post(self, request):
        username_or_email = request.POST['username']
        password = request.POST['password']
    
        if username_or_email and password:
            if "@" in username_or_email:
                user_ins = User.objects.filter(email=username_or_email).first()
                if user_ins:
                    username = user_ins.username
                else:
                    username = username_or_email
            else:
                username = username_or_email
            user=auth.authenticate(username=username,password=password)

            if user: 
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, '+user.username+' you are now logged in')
                    return redirect('leads')
                messages.error(request,'Account is not active, please check your email to activate account')
                return render(request,'authentication/login.html')
            messages.error(request,'Invalid Credentials')
            return render(request,'authentication/login.html')
        messages.error(request,'Please fill out all the fields')
        return render(request,'authentication/login.html')

@login_required(login_url="login")
def user_logout(request):
    auth.logout(request)
    return redirect("homepage")

