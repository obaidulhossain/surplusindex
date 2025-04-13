from django.shortcuts import render
from django.core.paginator import Paginator
from si_user.models import *
from .models import *
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# Create your views here.
def clientDetail(request):
    if request.method == 'POST':
        client = request.POST.get('client','')
    else:
        client = request.GET.get('client','')
    if client:
        client_instance = UserDetail.objects.get(pk=client)
        orders = client_instance.orders.all()
        for order in orders:
            deliveries = len(order.deliveries.all())
            delivered = len(order.deliveries.filter(delivery_status='delivered'))
            pending = deliveries - delivered
            order.undelivered_count = order.deliveries.exclude(delivery_status='delivered').count()
        

    context = {
        'client':client,
        'client_instance':client_instance,
        'orders':orders,
        'deliveries':deliveries,
        'delivered':delivered,
        'pending':pending,

    }
    return render(request, 'Admin_Client/client_detail.html', context)
@csrf_exempt
def updateDeliveryStatus(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            delivery_id = data.get('id')
            delivery_status = data.get('selected_Status')
            # Fetch the corresponding event object from the database
            delivery_instance = Deliveries.objects.get(id=delivery_id)
            delivery_instance.delivery_status = delivery_status
            delivery_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Deliveries.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Delivery instance not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def allClients(request):
    if request.method == 'POST':
        selectedClientType = request.POST.get('clientType','')
    else:
        selectedClientType = request.GET.get('clientType','')


    client_queryset = UserDetail.objects.all().prefetch_related('orders', 'orders__deliveries')
    if selectedClientType == 'manual_client':
        client_queryset = client_queryset.filter(user_type='manual_client')
    else:
        client_queryset = client_queryset.filter(user_type='si_client')

    for client in client_queryset:
        for order in client.orders.all():
            order.undelivered_count = order.deliveries.exclude(delivery_status='delivered').count()
            order.ready_count = order.deliveries.filter(delivery_status='ready').count()
            # Get the nearest delivery date
            nearest_delivery = order.deliveries.filter(delivery_date__isnull=False).aggregate(Min('delivery_date'))
            order.nearest_delivery_date = nearest_delivery['delivery_date__min']
    p = Paginator(client_queryset, 20)
    page = request.GET.get('page')
    clients = p.get_page(page)


    current_page = int(clients.number)
    second_previous = current_page + 2
    context = {
        'selectedClientType':selectedClientType,
        'clients':clients,

        'second_previous':second_previous,
    }
    return render(request, 'Admin_Client/all_clients.html', context)

@csrf_exempt
def updateOrderStatus(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            order_id = data.get('id')
            order_status = data.get('selected_Status')
            # Fetch the corresponding event object from the database
            order_instance = Orders.objects.get(id=order_id)
            order_instance.order_status = order_status
            order_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Order updated successfully!'})

        except Orders.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order instance not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)