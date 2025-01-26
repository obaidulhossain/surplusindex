from django.shortcuts import render, redirect
from . forms import CreateUserForm, LoginForm, UpdateUserForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# - authentication models and functions
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

# Create your views here.


# -- subscription view --
def subscription(request):
    if request.user.is_authenticated:
        return render(request, 'subscription.html')
    else:
        messages.success(request, "Must be logged in to update subscription settings!")
        return redirect('my-login')


# -- end of subscription view --

# -- Update User --
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form =UpdateUserForm(request.POST or None, instance=current_user)
        
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated Successfully!")
            return redirect('dashboard')
        
        context = {'user_form':user_form}

        return render(request, 'profile.html', context = context)    
    else:
        messages.success(request, "You must be logged in to access this page!")
        return redirect('my-login')
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



