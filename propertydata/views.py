from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AddPropertyForm
from .models import *
from django.http import HttpResponse
from django.core.paginator import Paginator
from si_user.models import UserDetail
from django.contrib import messages
from authentication.decorators import allowed_users
from Client.views import get_client_dashboard_context
from Admin.views import get_admin_dashboard_context


# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users

    group_function_mapping = {
        "admin": get_admin_dashboard_context,
        "clients": get_client_dashboard_context,
        # "researcher": get_researcher_dashboard_context,
        # "va": get_va_dashboard_context,
    }

    # Initialize an empty context
    context = {}

    # Loop through user groups and gather relevant context
    for group in request.user.groups.all():
        if group.name in group_function_mapping:
            group_context = group_function_mapping[group.name](request.user)
            context.update(group_context)

    return render(request, 'propertydata/dashboard.html', context)











#--------------view for My leads page ---------------------------------start
@login_required(login_url="login")
def myLeads(request):
    user = request.user
    # purchased_leads=Foreclosure.objects.filter(purchased_by=user).prefetch_related('status_for_lead')
    p = Paginator(Status.objects.filter(client=user, archived=False).prefetch_related('lead'),50)
    page = request.GET.get('page')
    leads = p.get_page(page)
    context = {
        'leads':leads,
        'user': user,
        # 'purchased_leads': purchased_leads,
        # 'statuses': statuses
        }
    return render(request, 'propertydata/myleads.html', context)
#--------------view for My leads page ---------------------------------end


#--------------Archive My Leads button action for My Leads Section ----------------Start    
def archive_mylead(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            status = Status.objects.get(pk=lead_id)
            status.archived = True
            status.save()
        messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully Archived! These leads can be found and unarchived from the Archived leads section.')
        return redirect('myleads')
    else:
        return HttpResponse("Invalid Request", status=400)
#--------------Archive My Leads button action for My Leads Section ----------------End    


#--------------view for Archived leads page ---------------------------------Start
def archivedLeads(request):
    user = request.user
    # purchased_leads=Foreclosure.objects.filter(purchased_by=user).prefetch_related('status_for_lead')
    p = Paginator(Status.objects.filter(client=user, archived=True).prefetch_related('lead'),50)
    page = request.GET.get('page')
    leads = p.get_page(page)
    
    context = {
        'leads':leads,
        'user': user,
        }
    return render(request, 'propertydata/archived.html', context)

#--------------view for Archived leads page ---------------------------------Start


#--------------Unrchive My Leads button action for Archived leads Section ----------------Start    
def unarchive_mylead(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            status = Status.objects.get(pk=lead_id)
            status.archived = False
            status.save()
        messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully Unarchived! And restored to My leads section.')
        return redirect('archived')
    else:
        return HttpResponse("Invalid Request", status=400)
#--------------Unrchive My Leads button action for Archived leads Section ----------------Start    



#--------------view for hidden leads page -----------------------------------start
def hiddenLeads(request):
    user = request.user
    p=Paginator(Foreclosure.objects.filter(hidden_for=user).exclude(purchased_by=user), 50)
    page = request.GET.get('page')
    leads = p.get_page(page)

    context = {
        'leads':leads,
        'user':user,
    }

    return render(request, 'propertydata/hiddenleads.html', context)
#--------------view for hidden leads page -----------------------------------end

#--------------unhide button action for Hidden Leads Section ----------------start
def unhideLeads(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            hideLeads = Foreclosure.objects.get(pk=lead_id)
            hideLeads.hidden_for.remove(request.user)
        messages.success(request,str(len(selected_leads_ids))+' Leads successfully unhidden and restored to All Leads section.')
        return redirect('hidden-leads')
    else:
        return HttpResponse("Invalid Request", status=400)
#--------------unhide button action for Hidden Leads Section ----------------end


def all_data(request):
    return render(request,'data/all_data.html')