from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse, HttpResponseRedirect
from . models import *
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

from tablib import Dataset
import pandas as pd
from django.contrib import messages
from .resources import ForeclosureEventsResource, ForeclosureEventsExportResource


# Create your views here.

def auctionCalendar(request):
    user = request.user
    userList = User.objects.filter(groups__name='researcher')
    if request.method == 'POST':
        selectedUser = request.POST.get('selectedUser','')
        stateFilter = request.POST.get('stateFilter','')
        countyFilter = request.POST.get('countyFilter','')
        saletypeFilter = request.POST.get('saletypeFilter','')
        saledateFilter = request.POST.get('saledateFilter','')
    else:
        selectedUser = request.GET.get('selectedUser','')
        stateFilter = request.GET.get('stateFilter','')
        countyFilter = request.GET.get('countyFilter','')
        saletypeFilter = request.GET.get('saletypeFilter','')
        saledateFilter = request.GET.get('saledateFilter','')
    
    event_queryset = foreclosure_Events.objects.all()
    states = event_queryset.values_list('state', flat=True).distinct()
    counties = event_queryset.values_list('county', flat=True).distinct()
    saletypes = event_queryset.values_list('sale_type', flat=True).distinct()
    
    if selectedUser:
        selectedUserinstance = User.objects.get(username=selectedUser)
        event_queryset = event_queryset.filter(assigned_to=selectedUserinstance)
        states = event_queryset.values_list('state', flat=True).distinct()
        counties = event_queryset.values_list('county', flat=True).distinct()
        saletypes = event_queryset.values_list('sale_type', flat=True).distinct()
    # else:
    #     event_queryset.filter(assigned_to=user)
    #     states = event_queryset.values_list('state', flat=True).distinct()
    #     counties = event_queryset.values_list('county', flat=True).distinct()

    if not stateFilter == "":
        event_queryset = event_queryset.filter(state=stateFilter)
        counties = event_queryset.values_list('county', flat=True).distinct()
        saletypes = event_queryset.values_list('sale_type', flat=True).distinct()
    
    if not countyFilter =="":
        event_queryset = event_queryset.filter(county=countyFilter)
        saletypes = event_queryset.values_list('sale_type', flat=True).distinct()
    
    if saletypeFilter:
        event_queryset = event_queryset.filter(sale_type=saletypeFilter)
    
    if saledateFilter == "past":
        event_queryset = event_queryset.filter(event_next__lt=now().date())
    elif saledateFilter == "upcoming":
        event_queryset = event_queryset.filter(event_next__gte=now().date())

    
    # Paginate the results
    total_events = event_queryset.count()
    p = Paginator(event_queryset, 20)
    page = request.GET.get('page')
    events = p.get_page(page)


    current_page = int(events.number)
    second_previous = current_page + 2

    context = {
        'userList':userList,
        'selectedUser':selectedUser,
        'stateFilter':stateFilter,
        'countyFilter':countyFilter,
        'saletypeFilter':saletypeFilter,
        'saledateFilter':saledateFilter,
        'events':events,
        'total_events':total_events,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'current_user':user,
        'second_previous':second_previous,
        }

    return render(request, 'auction_calendar/auction_calendar.html', context)



@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def update_row(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            event_id = data.get('id')
            event_next = data.get('event_next')
            event_updated_to = data.get('event_updated_to')
            event_updated_from = data.get('event_updated_from')

            # Fetch the corresponding event object from the database
            event = foreclosure_Events.objects.get(id=event_id)

            # Update the fields
            if event_next:
                event.event_next = event_next
            if event_updated_to:
                event.event_updated_to = event_updated_to
            if event_updated_from:
                event.event_updated_from = event_updated_from
            # Save the updated object
            event.save()

            # Respond with success
            
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except foreclosure_Events.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)




def calendarSettings(request):
    EventInstance = ""
    if request.method == 'POST':
        SelectedEvent = request.POST.get('selectedevent', '')
        
        State = request.POST.get('state','')
        County = request.POST.get('county','')
        Population = request.POST.get('population','')
        SaleType = request.POST.get('saletype','')
        EventStatus = request.POST.get('status','')
        EventLink = request.POST.get('eventlink','')
        CaseLink = request.POST.get('caselink','')
        UpdatedFrom = request.POST.get('updatedfrom','')
        UpdatedTo = request.POST.get('updatedto','')
        EventNext = request.POST.get('eventnext','')
        Assignedto = request.POST.get('assignedto','')

        if not SelectedEvent == "":
            EventInstance = foreclosure_Events.objects.get(pk=SelectedEvent)
            if State:
                EventInstance.state = State
            if County:
                EventInstance.county = County
            if Population:
                EventInstance.population = Population
            if SaleType:
                EventInstance.sale_type = SaleType
            if EventStatus:
                EventInstance.event_status = EventStatus
            if EventLink:
                EventInstance.event_site = EventLink
            if CaseLink:
                EventInstance.event_case_search = CaseLink
            if UpdatedFrom:
                EventInstance.event_updated_from = UpdatedFrom
            if UpdatedTo:
                EventInstance.event_updated_to = UpdatedTo
            if EventNext:
                EventInstance.event_next = EventNext
            if Assignedto:
                EventInstance.assigned_to = User.objects.get(pk=Assignedto)
            EventInstance.save()
            EventInstance.refresh_from_db()
            messages.success(request, "Event Updated!")
        else:
            EventInstance=foreclosure_Events.objects.create(
                state = State,
                county = County,
                population = Population,
                sale_type = SaleType,
                event_status = EventStatus
                )
            EventInstance.save()
            messages.success(request, "Event Created!")
    Users = User.objects.filter(groups__name='researcher')
    
    context = {
        'EventInstance' : EventInstance,
        'Users':Users,
    }
    
    return render(request, 'auction_calendar/calendar_settings.html', context)

def FilterEvents(request):

    State = request.GET.get('state', '')
    County = request.GET.get('county', '')
    SaleType = request.GET.get('sale_type', '')


    if not any([State, County, SaleType]):
        Events = foreclosure_Events.objects.all()[:0]
    else:
        Events = foreclosure_Events.objects.all()
    
    if State:
        Events = Events.filter(state__icontains=State)
    
    if County:
        Events = Events.filter(county__icontains=County)
    if SaleType:
        Events = Events.filter(sale_type__icontains=SaleType)
    

    results = list(Events.values('id', 'state','county','population', 'sale_type', 'event_status'))
    return JsonResponse({'Events': results})


@csrf_exempt
def DeleteEvent(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            EventID = data.get('Event_ID')           
            Event = foreclosure_Events.objects.get(pk=EventID)
            Event.delete()
            return JsonResponse({'status': 'success'})
        except foreclosure_Events.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def upload_file(request):
    if request.method == "POST":
        dataset = Dataset()
        new_file = request.FILES['file']

        event_resource = ForeclosureEventsResource()
        try:
            imported_data = dataset.load(new_file.read(), format='xlsx')
            result = event_resource.import_data(dataset, dry_run=True)

            if not result.has_errors():
                event_resource.import_data(dataset, dry_run=False)
                messages.success(request, 'Data import Successful!')
            else:
                messages.success(request, 'Error occured during import!')
        
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('upload_calendar_data')
    return render(request, 'auction_calendar/upload_file.html')
    

def export_data(request):
    resource = ForeclosureEventsExportResource()
    dataset = Dataset()# Export all data

    dataset = resource.export()

   # Prepare HTTP response for file download
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Auction_Event_Data.xlsx'
    return response

