from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AddPropertyForm
from .models import *
from django.http import HttpResponse
from django.core.paginator import Paginator
from si_user.models import UserDetail
from django.contrib import messages
from authentication.decorators import allowed_users


# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    return render(request, 'propertydata/dashboard.html')

@login_required(login_url="login")
def addProperty(request):
    form = AddPropertyForm()
    if request.method == 'POST':
        form = AddPropertyForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('addproperty')
    context = {'form':form}    
    return render(request, 'propertydata/addproperty.html')



#--------------view for All leads page ---------------------------------start
@login_required(login_url="login")
@allowed_users(allowed_roles=['admin', 'clients'])
def allLeads(request):
    user = request.user

    p=Paginator(Foreclosure.objects.exclude(hidden_for=user).exclude(purchased_by=user), 50)
    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    counties=Foreclosure.objects.values_list("county", flat=True).distinct()
    saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2
    

    context = {
        'leads':leads,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'second_previous':second_previous
        }

    return render(request, 'propertydata/allleads.html', context)
#--------------view for All leads page ---------------------------------end


#--------------Add to my Leads button action for All Leads Section ----------------start
def addtoMyList(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        lead_count = len(selected_leads_ids)
        
        # Get user credit details
        user_details = UserDetail.objects.get(user=request.user)
        free_credit = user_details.free_credit_balance
        purchased_credit = user_details.purchased_credit_balance
        
        # Check if user has enough credits
        total_credit = free_credit + purchased_credit
        if lead_count > total_credit:
            messages.error(request, "Insufficient credits to add the selected leads.")
            return redirect('leads')  # Redirect back to the leads page
        else:
            # Deduct credits
            remaining_leads = lead_count

            # Deduct from free credits first
            if free_credit >= remaining_leads:
                user_details.free_credit_balance -= remaining_leads
                remaining_leads = 0
                messages.info(request, str(lead_count) + ' Credits have been deducted from free credits')
                messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')

            else:
                if free_credit >= 1:

                    remaining_leads -= free_credit
                    user_details.free_credit_balance = 0
                    # Deduct the rest from purchased credits
                    user_details.purchased_credit_balance -= remaining_leads
                    messages.info(request, str(free_credit) + ' free credit and '+str(remaining_leads)+' purchased credit have beed deducted.') 
                    messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')
                else:
                    user_details.purchased_credit_balance -= remaining_leads
                    messages.info(request, str(remaining_leads)+' credits deducted from purchased credit balance.') 
                    messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')
            # Save updated credit balances
            user_details.save()
            user_details.update_total_credits()


            for lead_id in selected_leads_ids:
                Status.objects.create(lead_id=lead_id, client=request.user)
                fcl = Foreclosure.objects.get(pk=lead_id)
                fcl.purchased_by.add(request.user)
            return redirect('leads')
    else:
        return HttpResponse("Invalid Request", status=400)

#--------------Add to my Leads button action for All Leads Section ----------------End


#--------------Hide Leads button action for All Leads Section ----------------Start
def hidefromallLeads(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            hideLeads = Foreclosure.objects.get(pk=lead_id)
            hideLeads.hidden_for.add(request.user)
        messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully hidden from All Leads! Hidden leads can be found and unhidden from the Hidden leads section.')
        return redirect('leads')
        
    else:
        return HttpResponse("Invalid Request", status=400)
    
#--------------Hide Leads button action for All Leads Section ----------------End


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