from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from si_user.models import UserDetail

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)
            

    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('U are not allowed to access this page')
        return wrapper_func
    return decorator

def card_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):

        # Only check clients group
        if request.user.groups.filter(name="clients").exists():

            user_detail, created = UserDetail.objects.get_or_create(
                user=request.user
            )

            if user_detail.payment_method != UserDetail.ADDED:
                return redirect("add_card")

        return view_func(request, *args, **kwargs)

    return wrapper