from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect

from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse

from django.contrib import messages
from datetime import timedelta

# -----------Forms------------------

from propertydata.forms import *
# -----------Models------------------
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
    

    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    leads_queryset = Foreclosure.objects.filter(case_search_assigned_to=user)

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

    if status == "Pending":
        leads_queryset = leads_queryset.filter(case_search_status="Pending")
    elif status == "Completed":
        leads_queryset = leads_queryset.filter(case_search_status="Completed")
    elif status == "Verified":
        leads_queryset = leads_queryset.filter(case_search_status="Verified", changed_at__lt=now().date() - timedelta(days=7)).exclude(surplus_status='Fund Claimed').exclude(surplus_status='No Surplus').exclude(sale_status='Cancelled')
    



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
