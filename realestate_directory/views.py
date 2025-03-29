from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse
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


#old codes-------------------------------------
        # 'filter_option':filter_option, # Pass the current filter option to the template
        # 'option1':option1,
        # 'option2':option2,
        # 'option3':option3,
        # 'option4':option4,
        # 'selected_sale_types':selected_sale_types,
        # 'saletypetax':saletypetax,
        # 'saletypemtg':saletypemtg,
        # 'saletypeoth':saletypeoth,

    # all_states = foreclosure_Events.objects.values_list('state', flat=True).distinct()
    # # Get the filter option from the query parameters
    # filter_option = request.GET.get('filter', 'all')
    # state_selected = request.GET.get('states', 'All')
    # selected_sale_types = request.GET.getlist('sale_type')


    # option1 = ""
    # option2 = ""
    # option3 = ""
    # option4 = ""
    # saletypetax = False
    # saletypemtg = False
    # saletypeoth = False

    # if 'Tax' in selected_sale_types:
    #     saletypetax = True
    
    # if 'Mtg' in selected_sale_types:
    #     saletypemtg = True

    # if 'Oth' in selected_sale_types:
    #     saletypeoth = True
    
    # saletype_selected = []
    # if saletypetax:
    #     saletype_selected.append('Tax')
    # if saletypemtg:
    #     saletype_selected.append('Mortgage')
    # if saletypeoth:
    #     saletype_selected.append('Others')
    # # Determine the queryset based on the filter option
    
    # if filter_option == 'past':
    #     if state_selected == 'All' or state_selected == '':
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), sale_type__in=saletype_selected)
    #             option2="selected"
    #             option4 = 'All'
    #         else:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date())
    #             option2="selected"
    #             option4 = 'All'
    #     else:
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), state=state_selected, sale_type__in=saletype_selected)
    #             option2="selected"
    #             option4=state_selected
    #         else:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), state=state_selected)
    #             option2="selected"
    #             option4=state_selected
    # elif filter_option == 'upcoming':
    #     if state_selected == 'All' or state_selected == '':
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), sale_type__in=saletype_selected)
    #             option3="selected"
    #             option4='All'
    #         else:    
    #             events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date())
    #             option3="selected"
    #             option4='All'
    #     else:
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), state=state_selected, sale_type__in=saletype_selected)
    #             option3="selected"
    #             option4=state_selected
    #         else:    
    #             events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), state=state_selected)
    #             option3="selected"
    #             option4=state_selected
    # else:  # Default to 'all'
    #     if state_selected == 'All' or state_selected == '':
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(sale_type__in=saletype_selected)
    #             option1="selected"
    #             option4='All'                
    #         else:
    #             events_queryset = foreclosure_Events.objects.all()
    #             option1="selected"
    #             option4='All'
    #     else:
    #         if saletype_selected:
    #             events_queryset = foreclosure_Events.objects.filter(state=state_selected, sale_type__in=saletype_selected)
    #             option1="selected"
    #             option4=state_selected    
    #         else:
    #             events_queryset = foreclosure_Events.objects.filter(state=state_selected)
    #             option1="selected"
    #             option4=state_selected








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
    return render(request, 'auction_calendar/calendar_settings.html')




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

