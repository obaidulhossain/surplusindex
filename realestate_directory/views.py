from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse
from . models import *
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import json

from tablib import Dataset
import pandas as pd
from django.contrib import messages
from .resources import ForeclosureEventsResource, ForeclosureEventsExportResource
# Create your views here.

def auctionCalendar(request):

    user = request.user

    # Get the filter option from the query parameters
    filter_option = request.GET.get('filter', 'all')
    option1 = ""
    option2 = ""
    option3 = ""
    
    # Determine the queryset based on the filter option
    if filter_option == 'past':
        events_queryset = foreclosure_Events.objects.filter(tax_sale_next__lt=now().date())
        option2="selected"
    elif filter_option == 'upcoming':
        events_queryset = foreclosure_Events.objects.filter(tax_sale_next__gte=now().date())
        option3="selected"
    else:  # Default to 'all'
        events_queryset = foreclosure_Events.objects.all()
        option1="selected"

    
    # Paginate the results
    p = Paginator(events_queryset, 20)
    page = request.GET.get('page')
    events = p.get_page(page)


    current_page = int(events.number)
    second_previous = current_page + 2

    context = {
        'events':events,
        'second_previous':second_previous,
        'filter_option':filter_option, # Pass the current filter option to the template
        'option1':option1,
        'option2':option2,
        'option3':option3
        }

    return render(request, 'auction_calendar/auction_calendar.html', context)





@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def update_row(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            event_id = data.get('id')
            tax_sale_next = data.get('tax_sale_next')
            tax_sale_updated_to = data.get('tax_sale_updated_to')

            # Fetch the corresponding event object from the database
            event = foreclosure_Events.objects.get(id=event_id)

            # Update the fields
            if tax_sale_next:
                event.tax_sale_next = tax_sale_next
            if tax_sale_updated_to:
                event.tax_sale_updated_to = tax_sale_updated_to

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
    response['Content-Disposition'] = 'attachment; filename=Realestate_Directory_Database.xlsx'
    return response