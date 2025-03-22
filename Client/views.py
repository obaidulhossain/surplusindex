from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from authentication.decorators import allowed_users
from django.core.paginator import Paginator

from .models import *
from propertydata.models import *
from .forms import *
from .resources import *
# Create your views here.




def availableLeads(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        psmin = request.POST.get('ps_min','')
        vsmin = request.POST.get('vs_min','')
        showHidden = request.POST.get('show_hidden','')
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        psmin = request.GET.get('ps_min','')
        vsmin = request.GET.get('vs_min','')
        showHidden = request.GET.get('show_hidden','')


    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    leads_queryset = Foreclosure.objects.exclude(purchased_by=user)
    
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

    if showHidden != "show":
        leads_queryset = leads_queryset.exclude(hidden_for=user)
            
    
    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 5)
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {
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



def export_data(request):
    data = Foreclosure.objects.filter(surplus_status="Fund Available").prefetch_related('defendant__wireless', 'defendant__landline', 'defendant__emails')
    resources = ClientModelResource()
    dataset = resources.export(data)
    response = HttpResponse(dataset.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response