from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from . models import *
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users
from tablib import Dataset
import pandas as pd
from django.contrib import messages
from .resources import ForeclosureEventsResource, ForeclosureEventsExportResource


# Create your views here.
@login_required(login_url="login")
@allowed_users(['researcher', 'admin',])
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
    p = Paginator(event_queryset, 200)
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
            post_event_next = data.get('post_event_next')
            post_event_updated_to = data.get('post_event_updated_to')
            post_event_updated_from = data.get('post_event_updated_from')

            # Fetch the corresponding event object from the database
            event = foreclosure_Events.objects.get(id=event_id)

            # Update the fields
            if event_next:
                event.event_next = event_next
            if event_updated_to:
                event.event_updated_to = event_updated_to
            if event_updated_from:
                event.event_updated_from = event_updated_from

            if post_event_next:
                event.post_event_next = post_event_next
            if post_event_updated_to:
                event.post_event_updated_to = post_event_updated_to
            if post_event_updated_from:
                event.post_event_updated_from = post_event_updated_from
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



@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def update_row_post(request):
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
                event.post_event_next = event_next
            if event_updated_to:
                event.post_event_updated_to = event_updated_to
            if event_updated_from:
                event.post_event_updated_from = event_updated_from
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


@login_required(login_url="login")
@allowed_users(['admin'])
def calendarSettings(request):
    params = request.POST if request.method == "POST" else request.GET
    SelectedEvent = params.get('selectedevent', '')
    EventInstance = None

    if SelectedEvent:
        EventInstance = foreclosure_Events.objects.get(pk=SelectedEvent)

    Users = User.objects.filter(groups__name='researcher')
    
    context = {
        'EventInstance' : EventInstance,
        'Users':Users,
    }
    
    return render(request, 'auction_calendar/calendar_settings.html', context)


@login_required(login_url="login")
@allowed_users(['admin'])
def CreateUpdateEvents(request):
    params = request.POST if request.method == "POST" else request.GET
    SelectedEvent = params.get('selectedevent', '')

    State = params.get('state', '')
    County = params.get('county','')
    Population = params.get('population','')
    SaleType = params.get('saletype','')
    EventStatus = params.get('status','')
    EventLink = params.get('eventlink','')
    CaseLink = params.get('caselink','')
    UpdatedFrom = params.get('updatedfrom','')
    UpdatedTo = params.get('updatedto','')
    EventNext = params.get('eventnext','')
    PostUpdatedFrom = params.get('post_updatedfrom','')
    PostUpdatedTo = params.get('post_updatedto','')
    PostEventNext = params.get('post_eventnext','')
    Assignedto = params.get('assignedto','')
    Recorder = params.get('recorder','')
    Assessor = params.get('assessor','')
    TaxCollector = params.get('tax_collector','')
    GIS = params.get('gis','')
    District = params.get('district','')
    Civil = params.get('civil','')
    Municipal = params.get('municipal','')
    Probate = params.get('probate','')
    Superior = params.get('superior','')
    Supreme = params.get('supreme','')
    Surrogate = params.get('surrogate','')
    PublicNotice = params.get('public_notice','')
    
    EventInstance = None
    if SelectedEvent:
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
        if PostUpdatedFrom:
            EventInstance.post_event_updated_from = PostUpdatedFrom
        if PostUpdatedTo:
            EventInstance.post_event_updated_to = PostUpdatedTo
        if PostEventNext:
            EventInstance.post_event_next = PostEventNext
        if Recorder:
            EventInstance.recorder = Recorder
        if Assessor:
            EventInstance.assessor = Assessor
        if TaxCollector:
            EventInstance.tax_collector = TaxCollector
        if GIS:
            EventInstance.gis = GIS
        if District:
            EventInstance.district = District
        if Civil:
            EventInstance.civil = Civil
        if Municipal:
            EventInstance.municipal = Municipal
        if Probate:
            EventInstance.probate = Probate
        if Superior:
            EventInstance.superior = Superior
        if Supreme:
            EventInstance.supreme = Supreme
        if Surrogate:
            EventInstance.surrogate = Surrogate
        if PublicNotice:
            EventInstance.public_notice = PublicNotice
        if Assignedto:
            EventInstance.assigned_to = User.objects.get(pk=Assignedto)
        EventInstance.save()
        EventInstance.refresh_from_db()
        messages.success(request, "Event Updated!")
    else:
        EventInstance, created = foreclosure_Events.objects.get_or_create(
            state = State,
            county = County,
            sale_type = SaleType,
            defaults={
                "population" : Population,
                "event_status" : EventStatus,
            }
        )
        if created:
            messages.success(request, "Event Created!")
        else:
            messages.info(request, "Event already exist and selected")
    return redirect(f"{reverse('calendar_settings')}?selectedevent={EventInstance.id}")


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
    

    results = list(Events.values('id', 'state','county','population', 'sale_type', 'event_status','event_next','post_event_next'))
    return JsonResponse({'Events': results})


@login_required(login_url="login")
@allowed_users(['admin'])
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


@login_required(login_url="login")
@allowed_users(['admin'])
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
    

@login_required(login_url="login")
@allowed_users(['admin'])
def export_data(request):
    resource = ForeclosureEventsExportResource()
    dataset = Dataset()# Export all data

    dataset = resource.export()

   # Prepare HTTP response for file download
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Auction_Event_Data.xlsx'
    return response

