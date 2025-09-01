from django.shortcuts import render, redirect, HttpResponseRedirect
from propertydata.models import *
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db.models import Prefetch
from si_user.models import *
#----------------Data--------------------start
def get_admin_dashboard_context(request, user):
    transaction_queryset = UserTransactions.objects.all().order_by('-created_at')
    total_transactions = transaction_queryset.count()
    p = Paginator(transaction_queryset, 25)
    page = request.GET.get('page')
    Transactions = p.get_page(page)
    tr_current_page = int(Transactions.number)
    tr_second_previous = tr_current_page + 2
    context= {
        'Transactions':Transactions,
        'total_transactions':total_transactions,
        'tr_second_previous':tr_second_previous,
        
    }
    # Logic to get context data for client dashboard
    return context

def All_Contacts(request):
    user = request.user
    selectedUserInstance = User.objects.get(username=user)
    userList = User.objects.filter(groups__name='researcher')
    if request.method == 'POST':
        salestatusFilter = request.POST.get('salestatusFilter','')
        surplusstatusFilter = request.POST.get('surplusstatusFilter','')
        casesearchstatusFilter = request.POST.get('casesearchstatusFilter','')
        publishedstatusFilter = request.POST.get('publishedstatusFilter','')
        

        selectedUser = request.POST.get('selectedUser','')
        skiptraceStatus = request.POST.get('skiptraceStatus','')
        stateFilter = request.POST.get('stateFilter','')
        countyFilter = request.POST.get('countyFilter','')
        saletypeFilter = request.POST.get('saletypeFilter','')

        
        skp_assign_to = request.POST.get('skp_assign_to','')
        
        
    else:
        salestatusFilter = request.GET.get('salestatusFilter','')
        surplusstatusFilter = request.GET.get('surplusstatusFilter','')
        casesearchstatusFilter = request.GET.get('casesearchstatusFilter','')
        publishedstatusFilter = request.GET.get('publishedstatusFilter','')

        selectedUser = request.GET.get('selectedUser','')
        skiptraceStatus = request.GET.get('skiptraceStatus','')
        stateFilter = request.GET.get('stateFilter','')
        countyFilter = request.GET.get('countyFilter','')
        saletypeFilter = request.GET.get('saletypeFilter','')
    
    if selectedUser:
        if selectedUser == "none":
            filtered_defendants = Contact.objects.filter(skp_assignedto__isnull=True)
        else:
            filtered_defendants = Contact.objects.filter(skp_assignedto__username=selectedUser)
        if skiptraceStatus and skiptraceStatus == "Completed":
            filtered_defendants = filtered_defendants.filter(skiptraced=True)
        elif skiptraceStatus and skiptraceStatus == "Pending":
            filtered_defendants = filtered_defendants.filter(skiptraced=False)

        leads_queryset = Foreclosure.objects.prefetch_related(
            Prefetch(
                'defendant',  # related_name on Foreclosure -> Contact
                queryset=filtered_defendants,
                to_attr='filtered_defendants'  # this will hold the filtered results
            )
        )
    elif skiptraceStatus and skiptraceStatus == "Completed":
        filtered_defendants = Contact.objects.filter(skiptraced=True)
        leads_queryset = Foreclosure.objects.prefetch_related(
            Prefetch(
                'defendant',  # related_name on Foreclosure -> Contact
                queryset=filtered_defendants,
                to_attr='filtered_defendants'  # this will hold the filtered results
            )
        )
    elif skiptraceStatus and skiptraceStatus == "Pending":
        filtered_defendants = Contact.objects.filter(skiptraced=False)
        leads_queryset = Foreclosure.objects.prefetch_related(
            Prefetch(
                'defendant',  # related_name on Foreclosure -> Contact
                queryset=filtered_defendants,
                to_attr='filtered_defendants'  # this will hold the filtered results
            )
        )
    else:
        leads_queryset = Foreclosure.objects.all()
    # foreclosures = Foreclosure.objects.prefetch_related('defendant')


    # leads_queryset = Foreclosure.objects.all()

    

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

# update status--------------------------
    # if request.method == 'POST':

    #     if not skp_assign_to == "":
    #         i = 0
    #         userinstance = User.objects.get(username=skp_assign_to)
            
    #         for lead in leads_queryset:
    #             contacts_to_skp = lead.defendant.all()
    #             for contact in contacts_to_skp:
    #                     i += 1
    #                     if contact.skiptraced == False:
    #                         contact.skp_assignedto = userinstance
    #                         contact.save()
    #         messages.success(request, f"{i} Contacts from {len(leads_queryset)} Leads Assigned to {skp_assign_to} for skiptracing")


    total_leads = leads_queryset.count()

    all_def = set()
    for fcl in leads_queryset:
        if selectedUser:
            for contact in fcl.filtered_defendants:
                all_def.add(contact.id)
        else:
            for contact in fcl.defendant.all():
                all_def.add(contact.id)

    total_contacts = len(all_def)

    if request.method == 'POST':
        if not skp_assign_to == "":
            userinstance = User.objects.get(username=skp_assign_to)
            x = 0
            for i in all_def:
                Con_instance = Contact.objects.get(id=i)
                print(Con_instance.pk)
                if Con_instance.skiptraced == False:
                    x += 1
                    Con_instance.skp_assignedto = userinstance
                    Con_instance.save()
            messages.success(request, f"{x} Not skiptraced out of {total_contacts} contacts from {len(leads_queryset)} Leads Assigned to {skp_assign_to}")

        

    p = Paginator(leads_queryset, 100)
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
        'skiptraceStatus':skiptraceStatus,
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

        'all_def':all_def,
        'total_contacts':total_contacts,


    }
    return render(request, 'Admin/all_contacts.html', context)


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

        assignCaseSearch = request.POST.get('assignCaseSearch','')
        skp_assign_to = request.POST.get('skp_assign_to','')
        casesearchStatus = request.POST.get('casesearchStatus','')
        publishStatus = request.POST.get('publishStatus','')
        
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

# update status--------------------------
    if request.method == 'POST':
        if not assignCaseSearch == "":
            userinstance = User.objects.get(username=assignCaseSearch)
            for lead in leads_queryset:
                lead.case_search_assigned_to = userinstance
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Case Search Assigned to {assignCaseSearch}")

        if not skp_assign_to == "":
            i = 0
            userinstance = User.objects.get(username=skp_assign_to)
            
            for lead in leads_queryset:
                contacts_to_skp = lead.defendant.all()
                for contact in contacts_to_skp:
                        i += 1
                        if contact.skiptraced == False:
                            contact.skp_assignedto = userinstance
                            contact.save()
            messages.success(request, f"{i} Contacts from {len(leads_queryset)} Leads Assigned to {skp_assign_to} for skiptracing")

        if casesearchStatus == "Pending":
            for lead in leads_queryset:
                lead.case_search_status = "Pending"
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Case Search Status Changed to Pending")
        elif casesearchStatus == "Completed":
            for lead in leads_queryset:
                lead.case_search_status = "Completed"
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Case Search Status Changed to Completed")
        elif casesearchStatus == "Verified":
            for lead in leads_queryset:
                lead.case_search_status = "Verified"
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Case Search Status Changed to Verified")

        if publishStatus and publishStatus == "Unpublish":
            for lead in leads_queryset:
                lead.published = False
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Unpublished")
        elif publishStatus and publishStatus == "Publish":
            for lead in leads_queryset:
                lead.published = True
                lead.save()
            messages.success(request, f"{len(leads_queryset)} Leads Published")


    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 150)
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


@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def caseSearchStatus(request):

    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            fcl_id = data.get('id')
            selected_Status = data.get('selected_Status')
            

            # Fetch the corresponding event object from the database
            fcl_instance = Foreclosure.objects.get(id=fcl_id)

            # Update the fields
            if selected_Status:
                fcl_instance.case_search_status = selected_Status
            fcl_instance.save()

            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Foreclosure.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def publishStatus(request):  

    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            fcl_id = data.get('id')
            publish_Status = data.get('publish_Status')
            

            # Fetch the corresponding event object from the database
            fcl_instance = Foreclosure.objects.get(id=fcl_id)

            # Update the fields
            if publish_Status and fcl_instance.published == False:
                fcl_instance.published = True
                
            else:
                fcl_instance.published = False
                
            # Save the updated object
            fcl_instance.case_search_status = "verified"
            fcl_instance.save()

            # Respond with success
            
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Foreclosure.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def assignSKP(request):

    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            con_id = data.get('id')          
            assignto_User = data.get('assignto_User')
            # Fetch the corresponding event object from the database
            con_instance = Contact.objects.get(id=con_id)
            
            # Update the fields
            if assignto_User == "":
                con_instance.skp_assignedto = None
            else:
                try:
                    user_instance = User.objects.get(username=assignto_User)
                    con_instance.skp_assignedto = user_instance
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
            con_instance.save()


            # Respond with success
            
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Contact.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Contact not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def CreateUpdatePlan(request):
    plan = None
    if request.method == "POST":
        selectedPlan = request.POST.get('selected_plan',"")
        SubName = request.POST.get('sub_name',"")
        SubAmount = request.POST.get('sub_amount',"")
        SubProductid = request.POST.get('sub_stripe_product_id',"")
        SubType = request.POST.get('sub_type',"")
        SubPriceid= request.POST.get('sub_price_id',"")
        SubInterval= request.POST.get('sub_interval',"")
        SubDescription= request.POST.get('sub_description',"")
        SubActive= request.POST.get('sub_active',"False")
        SubBrochure = request.POST.get('brochure',"")
        if selectedPlan:
            PlanInstance = SubscriptionPlan.objects.get(pk=selectedPlan)
            PlanInstance.name = SubName
            PlanInstance.type = SubType
            PlanInstance.description = SubDescription
            PlanInstance.price_id = SubPriceid
            PlanInstance.stripe_product_id = SubProductid
            PlanInstance.amount = SubAmount
            PlanInstance.interval = SubInterval
            if SubActive == "True":
                PlanInstance.active = True
            else:
                PlanInstance.active = False
            PlanInstance.brochure = SubBrochure
            PlanInstance.save()
            plan = PlanInstance.pk
            messages.info(request, f"{SubName} Plan Updated")
        else:
            UpdatePlan, Created = SubscriptionPlan.objects.update_or_create(
                price_id=SubPriceid,
                defaults={
                    'name':SubName,
                    'type':SubType,
                    'description':SubDescription,
                    'stripe_product_id':SubProductid,
                    'amount':SubAmount,
                    'interval':SubInterval,
                    'active' : SubActive,
                    'brochure' : SubBrochure
                }
            )
            plan = UpdatePlan.pk
            if Created:
                messages.success(request, "A new Plan Created")
            else:
                messages.info(request, f"{SubName} Plan Updated")

    return HttpResponseRedirect(f"/manage_subscription/?selected_plan={plan}")

def SubscriptionSettings(request):
    AllPlans = SubscriptionPlan.objects.all().order_by('created_at')
    PlanInstance = None
    if request.method == "POST":
        selectedPlan = request.POST.get('selected_plan',"")
    else:
        selectedPlan = request.GET.get('selected_plan',"")
    if selectedPlan:
        PlanInstance = SubscriptionPlan.objects.get(pk=selectedPlan)
    

    context = {
        'SelectedPlan':PlanInstance,
        'Plans':AllPlans,
    }
    return render(request, 'Admin/manage_subs.html', context)

def ActiveSubscriptions(request):
    AvailablePlans = SubscriptionPlan.objects.all().order_by('name')
    Subscriptions = StripeSubscription.objects.all().order_by('current_period_end')
    if request.method == "POST":
        selectedPlan = request.POST.get('selectedPlan',"")
        Subscriptions = Subscriptions.filter(plan=selectedPlan)
    context = {
        'AvailablePlans':AvailablePlans,
        'Subscriptions':Subscriptions
    }
    return render(request, 'Admin/active_subs.html', context)