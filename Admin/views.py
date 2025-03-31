from django.shortcuts import render, redirect
from propertydata.models import *
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.


#----------------Data--------------------start




def All_Data(request):
# Filter foreclosure objects where published=False
    user = request.user
    selectedUserInstance = User.objects.get(username=user)
    userList = User.objects.filter(groups__name='researcher')
    if request.method == 'POST':
        salestatusFilter = request.POST.get('salestatusFilter','')
        surplusstatusFilter = request.POST.get('surplusstatusFilter','')
        casesearchstatusFilter = request.POST.get('casesearchstatusFilter','')
        publishedstatusFilter = request.POST.get('publishedstatusFilter','')

        selectedUser = request.POST.get('selectedUser','')
        stateFilter = request.POST.get('stateFilter','')
        countyFilter = request.POST.get('countyFilter','')
        saletypeFilter = request.POST.get('saletypeFilter','')

        assignCaseSearch = request.POST.get('')
        
        
        
    else:
        salestatusFilter = request.GET.get('salestatusFilter','')
        surplusstatusFilter = request.GET.get('surplusstatusFilter','')
        casesearchstatusFilter = request.GET.get('casesearchstatusFilter','')
        publishedstatusFilter = request.GET.get('publishedstatusFilter','')

        selectedUser = request.GET.get('selectedUser','')
        stateFilter = request.GET.get('stateFilter','')
        countyFilter = request.GET.get('countyFilter','')
        saletypeFilter = request.GET.get('saletypeFilter','')
        
    
    leads_queryset = Foreclosure.objects.all()
    if selectedUser:
        selectedUserInstance = User.objects.get(username=selectedUser)
        leads_queryset = leads_queryset.filter(case_search_assigned_to=selectedUserInstance)

    salestatuses = leads_queryset.values_list('sale_status', flat=True).distinct()
    surplusstatuses = leads_queryset.values_list('surplus_status', flat=True).distinct()
    casesearchstatuses = leads_queryset.values_list('case_search_status', flat=True).distinct()
    publishedstatuses = leads_queryset.values_list('published', flat=True).distinct()
    
    states = leads_queryset.values_list('state', flat=True).distinct()
    counties = leads_queryset.values_list('county', flat=True).distinct()
    saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()
    
    
    if salestatusFilter:
        leads_queryset = leads_queryset.filter(sale_status=salestatusFilter)
        
        states = leads_queryset.values_list('state', flat=True).distinct()
        counties = leads_queryset.values_list('county', flat=True).distinct()
        saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()


    if surplusstatusFilter:
        leads_queryset = leads_queryset.filter(surplus_status=surplusstatusFilter)
        
        states = leads_queryset.values_list('state', flat=True).distinct()
        counties = leads_queryset.values_list('county', flat=True).distinct()
        saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()
        
    if casesearchstatusFilter:
        leads_queryset = leads_queryset.filter(case_search_status=casesearchstatusFilter)
        
        states = leads_queryset.values_list('state', flat=True).distinct()
        counties = leads_queryset.values_list('county', flat=True).distinct()
        saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()
        
    if publishedstatusFilter:
        leads_queryset = leads_queryset.filter(published=publishedstatusFilter)
        
        states = leads_queryset.values_list('state', flat=True).distinct()
        counties = leads_queryset.values_list('county', flat=True).distinct()
        saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()
        
    if stateFilter:
        leads_queryset = leads_queryset.filter(state=stateFilter)
        counties = leads_queryset.values_list('county', flat=True).distinct()
        saletypes = leads_queryset.values_list('sale_type', flat=True).distinct()
       
    if countyFilter:
        leads_queryset = leads_queryset.filter(county=countyFilter)
      
    if saletypeFilter:
        leads_queryset = leads_queryset.filter(sale_type=saletypeFilter)

    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 30)
    page = request.GET.get('page')
    leads = p.get_page(page)


    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {       
        'leads':leads,
        'total_leads':total_leads,
        'second_previous':second_previous,
        'userList':userList,
        'selectedUser':selectedUser,
        'stateFilter':stateFilter,
        'countyFilter':countyFilter,
        'saletypeFilter':saletypeFilter,
        'salestatusFilter':salestatusFilter,
        'surplusstatusFilter':surplusstatusFilter,
        'casesearchstatusFilter':casesearchstatusFilter,
        'publishedstatusFilter':publishedstatusFilter,
        
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'salestatuses':salestatuses,
        'surplusstatuses':surplusstatuses,
        'casesearchstatuses':casesearchstatuses,
        'publishedstatuses':publishedstatuses,



    }
    return render(request, 'Admin/new_leads.html', context)

def assign_leads(request):
    assign_to = request.POST.get('assign_to')
    state = request.POST.get('sel_state')
    user = User.objects.get(username=assign_to)
    if state:
        leads_to_update = Foreclosure.objects.filter(published=False, state=state)
        if assign_to:
            for lead in leads_to_update:
                lead.case_search_assigned_to = user
                lead.save()
        else:
            messages.info(request, 'Please select a User to assign lead')
    else:
            messages.info(request, 'Please select a State to assign lead')

    return redirect('new_leads')

def update_case_search_status(request):
    status = request.POST.get('status')
    state = request.POST.get('sel_state')
    # user = User.objects.get(username=assign_to)
    if state:
        leads_to_update = Foreclosure.objects.filter(published=False, state=state)
        if status:
            for lead in leads_to_update:
                lead.case_search_status = status
                lead.save()
        else:
            messages.info(request, 'Please select a status to to update')
    else:
            messages.info(request, 'Please select a status to to update')

    return redirect('new_leads')

def update_publish_status(request):
    publish = request.POST.get('publish')
    state = request.POST.get('sel_state')
    # user = User.objects.get(username=assign_to)
    if state:
        if publish == "Publish":
            leads_to_update = Foreclosure.objects.filter(case_search_status="Pending", state=state) | Foreclosure.objects.filter(case_search_status="Completed", state=state)
            for lead in leads_to_update:
                lead.published = True
                lead.save()
        else:
            leads_to_update = Foreclosure.objects.filter(case_search_status="Pending", state=state) | Foreclosure.objects.filter(case_search_status="Completed", state=state)
            for lead in leads_to_update:
                lead.published = False
                lead.save()
    else:
            messages.info(request, 'Please select a state to to update')

    return redirect('new_leads')
#----------------Data--------------------end



def assign_skiptracing(request):
     
    assign_to = request.POST.get('skp_assign_to')
    state = request.POST.get('sel_state')
    user = User.objects.get(username=assign_to)
    if state:
        foreclosures = Foreclosure.objects.filter(state=state)
        if assign_to:
            for foreclosure in foreclosures:
                print(foreclosure.case_number)
                contacts_to_update = foreclosure.defendant.all()
                for contact in contacts_to_update:
                     if contact.skiptraced == False:
                          contact.skp_assignedto.add(user)
                          contact.save()
        else:
            messages.info(request, 'Please select a User to assign Skiptracing')
    else:
            messages.info(request, 'Please select a State to assign Skiptracing')

    return redirect('new_leads')


