from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AddPropertyForm
from .models import Court_Record, Foreclosure, Status
from django.http import HttpResponse
from django.core.paginator import Paginator


# Create your views here.
@login_required(login_url="login")
def index(request):
    return render(request, 'propertydata/index.html')

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

@login_required(login_url="login")
def allLeads(request):
    user = request.user
    #fcl = Foreclosure.objects.exclude(hidden_for=user).exclude(purchased_by=user)
    p=Paginator(Foreclosure.objects.exclude(hidden_for=user).exclude(purchased_by=user), 100)
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


def addtoMyList(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            add_leads = Status.objects.create()
            purchased = Foreclosure.objects.get(pk=lead_id)
            add_leads.lead.add(Foreclosure.objects.get(pk=lead_id))
            add_leads.client.add(request.user)
            purchased.purchased_by.add(request.user)
        return redirect('leads')
    else:
        return HttpResponse("Invalid Request", status=400)


def hidefromallLeads(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')

        for lead_id in selected_leads_ids:
            hideLeads = Foreclosure.objects.get(pk=lead_id)
            hideLeads.hidden_for.add(request.user)
        return redirect('leads')
    else:
        return HttpResponse("Invalid Request", status=400)