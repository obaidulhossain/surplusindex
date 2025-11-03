from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from si_user.models import *
from .models import *
from propertydata.models import *
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from Admin.utils.sessions import get_logged_in_users
from django.utils.timezone import now
import json
from django.contrib import messages
from datetime import date
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from authentication.utils import token_generator
from Admin_Client.models import UserDetail


def allClients(request):
    today_date = date.today()
    if request.method == 'POST':
        selectedClientType = request.POST.get('clientType','')
        active_status = request.POST.get('active_status','')
    else:
        selectedClientType = request.GET.get('clientType','')
        active_status = request.GET.get('active_status','')


    client_queryset = UserDetail.objects.all().order_by('-created_at').prefetch_related('orders', 'orders__deliveries')
    if selectedClientType == 'manual_client':
        client_queryset = client_queryset.filter(user_type='manual_client')
    else:
        client_queryset = client_queryset.filter(user_type='si_client')

    if active_status and active_status =="active":
        client_queryset = client_queryset.filter(user__is_active=True)
    elif active_status and active_status =="inactive":
        client_queryset = client_queryset.filter(user__is_active=False)

    for client in client_queryset:
        client.total_orders = client.orders.all().count
        client.total_running = client.orders.filter(order_status="running").count
        client.total_completed = client.orders.filter(order_status="completed").count
     
        for order in client.orders.all():
            order.undelivered_count = order.deliveries.exclude(delivery_status='delivered').count()
            order.ready_count = order.deliveries.filter(delivery_status='ready').count()
            # Get the nearest delivery date
            nearest_delivery = order.deliveries.filter(delivery_date__isnull=False).aggregate(Min('delivery_date'))
            order.nearest_delivery_date = nearest_delivery['delivery_date__min']
    total_client = client_queryset.count()
    p = Paginator(client_queryset, 20)
    page = request.GET.get('page')
    clients = p.get_page(page)


    current_page = int(clients.number)
    second_previous = current_page + 2
    context = {
        'selectedClientType':selectedClientType,
        'clients':clients,
        'today_date':today_date,
        'second_previous':second_previous,
        'total_client':total_client,
        'active_status':active_status,
    }
    return render(request, 'Admin_Client/all_clients.html', context)

def updateCredits(request):
    if request.method == "POST":
        count = 0
        selectedClientType = request.POST.get('clientType')

        if selectedClientType in ["si_client", "manual_client"]:
            clients = UserDetail.objects.filter(user__groups__name='clients', user_type=selectedClientType)

            for client in clients:
                client.update_total_credits()
                count += 1

            messages.success(request, f"Credits updated for {count} clients.")
        else:
            messages.error(request, "Invalid client type selected.")

        return HttpResponseRedirect(f"/all_clients/?clientType={selectedClientType}")

    return HttpResponseRedirect("/all_clients/")



def clientDetail(request):
    deliveries = ""
    delivered = ""
    pending = ""

    if request.method == 'POST':
        client = request.POST.get('client','')
        selected_orderstatus = request.POST.get('order-status','')
    else:
        client = request.GET.get('client','')
        selected_orderstatus = request.GET.get('order-status','')
    if client:
        client_instance = UserDetail.objects.get(pk=client)
        stat_instance = UserDetail.objects.get(pk=client)
        running_orders = len(stat_instance.orders.filter(order_status='running'))
        completed_orders = len(stat_instance.orders.filter(order_status='completed'))
        total_order_amount = stat_instance.orders.aggregate(total_amount=Sum('order_price'))['total_amount']
        total_paid = stat_instance.orders.filter(payment_status=Orders.PAID).aggregate(paid_amount=Sum('order_price'))['paid_amount']
        total_unpaid = stat_instance.orders.exclude(payment_status=Orders.PAID).aggregate(unpaid_amount=Sum('order_price'))['unpaid_amount']

        purchased_leads = Foreclosure.objects.filter(purchased_by = client_instance.user)
        total_purchased = len(purchased_leads)
        active = len(purchased_leads.filter(sale_status = "Active"))
        sold = len(purchased_leads.filter(sale_status = "Sold"))
        cancelled = len(purchased_leads.filter(sale_status = "Cancelled"))
        bankruptcy = len(purchased_leads.filter(sale_status = "Bankruptcy Hold"))
        sold_to_plt = len(purchased_leads.filter(sale_status = "Sold To Plaintiff"))

        possible_surplus = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "Possible Surplus"))
        verified_surplus = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "Fund Available"))
        not_determined = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "Not Determined"))
        no_possible_surplus = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "No Possible Surplus"))
        motion_filed = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "Motion Filed"))
        fund_claimed = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "Fund Claimed"))
        no_surplus = len(purchased_leads.filter(sale_status = "Sold", surplus_status = "No Surplus"))




        orders = client_instance.orders.all()
        if selected_orderstatus and selected_orderstatus == "running":
            orders = orders.filter(order_status="running")
        elif selected_orderstatus and selected_orderstatus == "completed":
            orders = orders.filter(order_status="completed")
        
        
        for order in orders:
            
            deliveries = len(order.deliveries.all())
            delivered = len(order.deliveries.filter(delivery_status='delivered'))
            pending = deliveries - delivered
            order.undelivered_count = order.deliveries.exclude(delivery_status='delivered').count()
        user_instance = client_instance.user
        logged_in_users = get_logged_in_users()
        login_status = "Online" if user_instance in logged_in_users else user_instance.last_login


    context = {
        'client':client,
        'client_instance':client_instance,
        'selected_orderstatus':selected_orderstatus,
        'all_orders':len(orders),
        'running_orders':running_orders,
        'completed_orders':completed_orders,
        'total_order_amount':total_order_amount,
        'total_paid':total_paid,
        'total_unpaid':total_unpaid,
        'orders':orders,
        'deliveries':deliveries,
        'delivered':delivered,
        'pending':pending,
        'login_status':login_status,

        'total_purchased':total_purchased,
        'active':active,
        'sold':sold,
        'cancelled':cancelled,
        'bankruptcy':bankruptcy,
        'sold_to_plt':sold_to_plt,
        'possible_surplus':possible_surplus,
        'verified_surplus':verified_surplus,
        'not_determined':not_determined,
        'no_possible_surplus':no_possible_surplus,
        'motion_filed':motion_filed,
        'fund_claimed':fund_claimed,
        'no_surplus':no_surplus,

    }
    return render(request, 'Admin_Client/client_detail.html', context)



def clientSettings(request):
    if request.method == 'POST':
        client = request.POST.get('client','')
    else:
        client = request.GET.get('client','')
    context = {

    }
    return render(request, 'Admin_Client/client_settings.html', context)

def registerClient(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        customer_id = request.POST.get('customer_id','')
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active=True
                user.first_name = first_name
                user.last_name = last_name
                user.groups.add(Group.objects.get(name='clients'))
                user.save()
                userinstance = User.objects.get(username=username)
                if not UserDetail.objects.filter(user=userinstance).exists():
                    userdetail = UserDetail.objects.create(
                        user = userinstance,
                        phone = phone,
                        user_type = "manual_client",
                        customer_id = customer_id,
                    )
                else:
                    userdetail = UserDetail.objects.get(user__username=username)
                    userdetail.phone = phone
                    userdetail.user_type = "manual_client"
                    userdetail.stripe_customer_id = customer_id,

                userdetail.update_total_credits()
                userdetail.save()

                messages.success(request, 'Client Instance Created')
            else:
                messages.success(request, 'Email already Exist')
        else:
            messages.success(request, 'Username already Exist')
    return redirect ('client_settings')





def CreateOrder(request):
    if request.method == 'POST':
        client = request.POST.get('client','')
        client_instance = UserDetail.objects.get(pk=client)
        User_instance = User.objects.get(pk=client_instance.user.pk)
        selected_orderstatus = request.POST.get('order-status','')
        
        order_date = request.POST.get('order-date','')
        order_status = request.POST.get('status','')
        order_price = request.POST.get('order_price','')
        payment_status = request.POST.get('payment-status','')
        payment_method = request.POST.get('payment-method','')
        order_detail = request.POST.get('order-detail','')

        customer_id = request.POST.get('customer_id','')
        checkout_id = request.POST.get('checkout_id','')

        transaction = UserTransactions.objects.create(
            user = User_instance,
            stripe_customer_id = customer_id,
            stripe_checkout_id = checkout_id,
            amount = order_price,
            number_of_leads = order_price,
            currency = "USD",
            has_paid = True if payment_status == "paid" else False,
        )
        transaction.save()

        order_instance = Orders.objects.create(
            date_ordered = order_date,
            order_detail = order_detail,
            order_status = order_status,
            order_price = order_price,
            payment_method = payment_method,
            payment_status = payment_status,
            transaction = transaction,
        )
        
        order_instance.save()
        client_instance.orders.add(order_instance)
        client_instance.purchased_credit_balance = client_instance.purchased_credit_balance + int(order_price)
        client_instance.update_total_credits()
        client_instance.save()
        

        return HttpResponseRedirect(f"/client_detail/?client={client}&order-status={selected_orderstatus}")
    return redirect('client_detail')

def UpdatePaymentStatus(request):
    if request.method == 'POST':
        client = request.POST.get('client','')
        selected_orderstatus = request.POST.get('order-status','')
        order = request.POST.get('order','')
        Selected_Status = request.POST.get('payment-status','')

        order_instance = Orders.objects.get(pk=order)
        transaction_instance = UserTransactions.objects.get(pk=order_instance.transaction.id)
        if Selected_Status == "paid":
            transaction_instance.has_paid = True
        else:
            transaction_instance.has_paid = False
        transaction_instance.save()
         
        order_instance.payment_status = Selected_Status
        order_instance.save()
        return HttpResponseRedirect(f"/client_detail/?client={client}&order-status={selected_orderstatus}")
    return redirect('client_detail')


def createDelivery(request):
    if request.method == "POST":
        client_id = request.POST.get('client_id','')
        order_id = request.POST.get('order_id', '')
        delivery_date = request.POST.get('delivery_date','')
        delivery_note = request.POST.get('delivery_note', '')
        delivered_date = request.POST.get('delivered_date','')
        delivery_status = request.POST.get('delivery_status', '')

        delivery_instance = Deliveries.objects.create(
            delivery_date = delivery_date,
            delivery_status = delivery_status,
            delivery_note = delivery_note,
        )
        if not delivered_date == "":
            delivery_instance.delivered_in = delivered_date
        
            
            
        
        delivery_instance.save()
        order_instance = Orders.objects.get(pk=order_id)
        order_instance.deliveries.add(delivery_instance)
    return HttpResponseRedirect (f"/client_detail/?client={client_id}")

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



@require_POST
def resend_activation_email(request):
    user_id = request.POST.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'Missing user_id'})

    try:
        user = User.objects.get(id=user_id)
        detail = getattr(user, 'credits', None)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})

    if user.is_active:
        return JsonResponse({'success': False, 'error': 'Already active'})

    if detail and detail.activation_attempt >= 3:
        return JsonResponse({'success': False, 'error': 'Attempt limit reached'})

    # build activation link
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
    activate_url = f"http://{domain}{link}"

    # send mail
    send_mail(
        "Resend Activation - SurplusIndex",
        f"Hi {user.username},\n\nPlease use this link to activate your account:\n{activate_url}",
        "contact@surplusindex.com",
        [user.email],
        fail_silently=False
    )

    # increment attempts
    if detail:
        detail.activation_attempt += 1
        detail.save()

    return JsonResponse({
        'success': True,
        'message': f"Email sent to {user.email}",
        'attempts': detail.activation_attempt if detail else 1
    })