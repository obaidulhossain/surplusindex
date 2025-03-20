from django.shortcuts import render, redirect
from propertydata.models import *
from django.contrib import messages

# Create your views here.


#----------------Data--------------------start
def newly_added_leads(request):
# Filter foreclosure objects where published=False
    NewLeads = Foreclosure.objects.filter(published=False)
    
    # Extract unique states and dates
    States = NewLeads.values('state').distinct()
    sel_state = request.POST.get('sel_state', '')
    
    # Filter by selected state if provided
    if sel_state:
        NewLeads = NewLeads.filter(state=sel_state)

    # Researchers
    DA = User.objects.filter(groups__name='researcher')

    context = {
        'NewLeads':NewLeads,
        'DA':DA,
        'States':States,
        'sel_state':sel_state,
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


