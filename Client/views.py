from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from authentication.decorators import allowed_users
from django.core.paginator import Paginator
from django.contrib import messages

from .models import *
from propertydata.models import *
from .forms import *
from .resources import *
from si_user.models import *
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



def availableLeads(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        psmin = request.POST.get('ps_min','')
        vsmin = request.POST.get('vs_min','')
        showHidden = request.POST.get('show_hidden','')
        showUpcoming = request.POST.get('show_upcoming','')
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        psmin = request.GET.get('ps_min','')
        vsmin = request.GET.get('vs_min','')
        showHidden = request.GET.get('show_hidden','')
    

    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    leads_queryset = Foreclosure.objects.exclude(purchased_by=user).exclude(sale_status="CANCELLED" or "ACTIVE").exclude(surplus_status= "NO_SURPLUS" or None)
    
    if not selectedState:
        counties=Foreclosure.objects.values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()

    else:
        counties=Foreclosure.objects.filter(state=selectedState).values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.filter(state=selectedState).values_list("sale_type", flat=True).distinct()
        leads_queryset = leads_queryset.filter(state__iexact=selectedState)

    if selectedCounty:
        leads_queryset = leads_queryset.filter(county__iexact=selectedCounty)

    if selectedSaletype:
        leads_queryset = leads_queryset.filter(sale_type__iexact=selectedSaletype)

    if psmin:
        leads_queryset = leads_queryset.filter(possible_surplus__gte=psmin)

    if vsmin:
        leads_queryset = leads_queryset.filter(verified_surplus__gte=vsmin)

    if not showHidden == "show":
        leads_queryset = leads_queryset.exclude(hidden_for=user)
    else:
        leads_queryset = leads_queryset.filter(hidden_for=user)



    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 25)
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {
        'current_user':user,
        'leads':leads,
        'total_leads':total_leads,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
        'psmin':psmin,
        'vsmin':vsmin,
        'showHidden':showHidden,

        'second_previous':second_previous
    }
    return render(request, 'Client/available_leads.html', context)

def purchaseLeads(request):
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

def hidefromallLeads(request):
    selectedState = request.POST.get('stateFilter','')
    selectedCounty = request.POST.get('countyFilter','')
    selectedSaletype = request.POST.get('saletypeFilter','')
    psmin = request.POST.get('ps_min','')
    vsmin = request.POST.get('vs_min','')
    unhide = request.POST.get('unhide')
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        if unhide == "show":
            for lead_id in selected_leads_ids:
                unhideLeads = Foreclosure.objects.get(pk=lead_id)
                unhideLeads.hidden_for.remove(request.user)
            messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully unhidden from All Leads! ')
        
        else:
            for lead_id in selected_leads_ids:
                hideLeads = Foreclosure.objects.get(pk=lead_id)
                hideLeads.hidden_for.add(request.user)
            messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully hidden from All Leads! ')
        return redirect('leads')

    else:
        return HttpResponse("Invalid Request", status=400)

def myLeads(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        psmin = request.POST.get('ps_min','')
        vsmin = request.POST.get('vs_min','')
        showArchived = request.POST.get('show_archived','')
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        psmin = request.GET.get('ps_min','')
        vsmin = request.GET.get('vs_min','')
        showArchived = request.GET.get('show_Archived','')
    

    statusinstances = Status.objects.filter(client=user)
    leads_queryset = Foreclosure.objects.filter(foreclosure_as_lead__in=statusinstances).prefetch_related('foreclosure_as_lead')
    states=leads_queryset.values_list("state", flat=True).distinct()
    if not selectedState:
        counties=Foreclosure.objects.values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()

    else:
        counties=Foreclosure.objects.filter(state=selectedState).values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.filter(state=selectedState).values_list("sale_type", flat=True).distinct()
        leads_queryset = leads_queryset.filter(state__iexact=selectedState)
    
    if not showArchived == "show":
        leads_queryset = leads_queryset.exclude(archived_by=user)
    else:
        leads_queryset = leads_queryset.filter(archived_by=user)

    if selectedCounty:
        leads_queryset = leads_queryset.filter(county__iexact=selectedCounty)

    if selectedSaletype:
        leads_queryset = leads_queryset.filter(sale_type__iexact=selectedSaletype)

    if psmin:
        leads_queryset = leads_queryset.filter(possible_surplus__gte=psmin)

    if vsmin:
        leads_queryset = leads_queryset.filter(verified_surplus__gte=vsmin)

    



    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 25)
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {
        'current_user':user,
        'leads':leads,
        'total_leads':total_leads,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
        'psmin':psmin,
        'vsmin':vsmin,
        'showArchived':showArchived,

        'second_previous':second_previous
    }
    return render(request, 'Client/my_leads.html', context)


def archivefromMyLeads(request):
    showArchived = request.POST.get('show_archived','')
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        
        for lead_id in selected_leads_ids:
            fclinstance = Foreclosure.objects.get(pk=lead_id)
            if not request.user in fclinstance.archived_by.all():
                fclinstance.archived_by.add(request.user)

            else:
                fclinstance.archived_by.remove(request.user)
        if showArchived == 'show':
            messages.success(request, str(len(selected_leads_ids)) + ' Leads unarchived!')
        else:
            messages.success(request, str(len(selected_leads_ids)) + ' Leads archived!')
        return redirect('myleads')
    else:
        return HttpResponse("Invalid Request", status=400)


def leadsDetail(request):
    if request.method == "POST":
        selected_status = request.POST.get('status_id')
        status_instance = Status.objects.get(pk=selected_status)
        numberinuse = request.POST.get('numberinuse','')

        status_instance.number_in_use = numberinuse
        status_instance.save()
        messages.info(request, 'Status Updated')
    else:
        selected_status = request.GET.get('status_id')
    
    status_instance = Status.objects.get(pk=selected_status)
    alldef = status_instance.lead.defendant.all()
    allplt = status_instance.lead.plaintiff.all()
    alladdress = status_instance.lead.property.all()
    
    context = {
        
        'status_instance':status_instance,
        'alldef':alldef,
        'allplt':allplt,
        'alladdress':alladdress,

        # 'fcl_instance':fcl_instance,
    }
    return render(request, 'Client/leads-detail.html', context)
    

def updateStatus(request):
    selected_status = request.POST.get('status_id')
    status_instance = Status.objects.get(pk=selected_status)
    numberinuse = request.POST.get('numberinuse','')

    status_instance.number_in_use = numberinuse
    status_instance.save()

    return redirect('leads-detail')



def export_data(request):
    data = Foreclosure.objects.filter(surplus_status="Fund Available").prefetch_related('defendant__wireless', 'defendant__landline', 'defendant__emails')
    resources = ClientModelResource()
    dataset = resources.export(data)
    response = HttpResponse(dataset.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response