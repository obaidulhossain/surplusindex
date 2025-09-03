from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect

from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse

from django.contrib import messages
from datetime import timedelta

# -----------Forms------------------

from propertydata.forms import *
# -----------Models----------------
from django.db.models import Prefetch
from . models import *
from realestate_directory.models import *
from propertydata.models import *

def caseChecklist(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        status = request.POST.get('casestatusFilter','')
        

        
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        status = request.GET.get('casestatusFilter','')
    

    # states=Foreclosure.objects.values_list("state", flat=True).distinct()

    leads_queryset = Foreclosure.objects.filter(case_search_assigned_to=user)
    if status == "pending":
        leads_queryset = leads_queryset.filter(case_search_status="pending")
    elif status == "completed":
        leads_queryset = leads_queryset.filter(case_search_status="completed")
    elif status == "verified":
        leads_queryset = leads_queryset.filter(case_search_status="verified", changed_at__lt=now().date() - timedelta(days=7)).exclude(surplus_status='fund claimed').exclude(surplus_status='no surplus').exclude(sale_status='cancelled')
    
    states = leads_queryset.values_list("state", flat=True).distinct()
    counties=leads_queryset.values_list("county", flat=True).distinct()
    saletypes=leads_queryset.values_list("sale_type", flat=True).distinct()


    if selectedState:
        leads_queryset = leads_queryset.filter(state__iexact=selectedState)
        counties=leads_queryset.values_list("county", flat=True).distinct()
        saletypes=leads_queryset.values_list("sale_type", flat=True).distinct()
        

    if selectedCounty:
        leads_queryset = leads_queryset.filter(county__iexact=selectedCounty)
        saletypes=leads_queryset.values_list("sale_type", flat=True).distinct()

    if selectedSaletype:
        leads_queryset = leads_queryset.filter(sale_type__iexact=selectedSaletype)




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
        'status':status,

        'second_previous':second_previous
    }
    return render(request, 'da/active_tasks.html', context)




# Create your views here.

def SkiptracingChecklist(request):

    current_user = request.user
    params = request.POST if request.method == "POST" else request.GET
    selectedState = params.get('stateFilter', '')
    selectedCounty = params.get('countyFilter', '')
    selectedSaletype = params.get('saletypeFilter', '')

    #--------------------Queryset---------------------------------------------------------------
    # Get foreclosure records linked to contacts assigned to the current user and not skiptraced
    foreclosure_qs = (
        Foreclosure.objects
        .filter(defendant__skp_assignedto=current_user, defendant__skiptraced=False)
        .prefetch_related(
            Prefetch(
                "defendant",
                queryset=Contact.objects.filter(skp_assignedto=current_user, skiptraced=False),
                to_attr="pending_contacts"
            )
        )
        .distinct()
    )
    #-------------------------------------------------------------------------------------------

    #---------------Filters-----------------------------
    filters = {}
    if selectedState:
        filters["state__iexact"] = selectedState
    if selectedCounty:
        filters["county__iexact"] = selectedCounty
    if selectedSaletype:
        filters["sale_type__iexact"] = selectedSaletype
    foreclosure_qs = foreclosure_qs.filter(**filters)
    #---------------------------------------------------

    # Pagination
    p = Paginator(foreclosure_qs, 20)
    page = request.GET.get('page')
    checklist = p.get_page(page)

    current_page = int(checklist.number)
    second_previous = current_page + 2 if checklist.has_next() else None

    # Dropdown filters
    states = foreclosure_qs.values_list("state", flat=True).distinct()
    counties = foreclosure_qs.values_list("county", flat=True).distinct()
    saletypes = foreclosure_qs.values_list("sale_type", flat=True).distinct()
    

    context = {
        'current_user': current_user,
        'checklist': checklist,
        'states': states,
        'counties': counties,
        'saletypes': saletypes,
        'second_previous': second_previous,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
    }
    return render(request, 'da/active_skp.html', context)
