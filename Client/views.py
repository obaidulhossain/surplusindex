from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from authentication.decorators import allowed_users
from django.core.paginator import Paginator
from django.contrib import messages

from .models import *
from propertydata.models import *
from .forms import *
from .resources import *
from si_user.models import *
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .constants import *
from django.db.models import Count, Q
from datetime import date
from urllib.parse import urlencode
from django.urls import reverse

def get_client_dashboard_context(request, user):
    statuses = Status.objects.filter(client=user)
    activeLeads = statuses.filter(archived=False).exclude(closing_status__in=['closed_funded', 'closed_not_funded'])
    closedLeads = statuses.filter(closing_status__in=['closed_funded', 'closed_not_funded'])
    archivedLeads = statuses.filter(archived=True)
    closingDeals = activeLeads.filter(closing_status = 'conversion_in_progress')
    activeProspecting = activeLeads.exclude(find_contact_status='not_assigned').exclude(closing_status = 'conversion_in_progress')
    notAssigned = activeLeads.filter(find_contact_status='not_assigned')

    
    stateData = (
        Foreclosure.objects.values('state').exclude(published=False).exclude(surplus_status__in=['fund claimed', 'no surplus'])
        .annotate(
            total_count = Count('id'),
            tax_count = Count('id', filter=Q(sale_type='tax')),
            mortgage_count=Count('id', filter=Q(sale_type='mortgage')),


        )
        .order_by('state')
    )

    Actions = ActionHistory.objects.filter(client=user).order_by('-created_at')[:50]

    Followups = FollowUp.objects.filter(client=user).exclude(f_status='completed').order_by('followup_date')
    for item in Followups:
        item.is_past_due = item.followup_date and item.followup_date < date.today()
    userDetail = UserDetail.objects.get(user=user)
    context= {
        'statuses':statuses,
        'userDetail':userDetail,
        'activeLeads':activeLeads,
        'closedLeads':closedLeads,
        'archivedLeads':archivedLeads,
        'closingDeals':closingDeals,
        'activeProspecting':activeProspecting,
        'notAssigned':notAssigned,
        'stateData':stateData,
        'Actions':Actions,
        'Followups':Followups,
    }
    # Logic to get context data for client dashboard
    return context





def availableLeads(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        psmin = request.POST.get('ps_min','')
        vsmin = request.POST.get('vs_min','')
        showHidden = request.POST.get('show_hidden','')
        showUpcoming = request.POST.get('show_upcoming','')
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        psmin = request.GET.get('ps_min','')
        vsmin = request.GET.get('vs_min','')
        showHidden = request.GET.get('show_hidden','')
    

    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    leads_queryset = Foreclosure.objects.exclude(purchased_by=user).exclude(sale_status="Cancelled").exclude(sale_status="Active").exclude(surplus_status="No Surplus").exclude(surplus_status=None).exclude(published=False)
    
    if not selectedState:
        counties=Foreclosure.objects.values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()

    else:
        counties=Foreclosure.objects.filter(state=selectedState).values_list("county", flat=True).distinct()
        saletypes=Foreclosure.objects.filter(state=selectedState).values_list("sale_type", flat=True).distinct()
        leads_queryset = leads_queryset.filter(state__iexact=selectedState)

    if selectedCounty:
        leads_queryset = leads_queryset.filter(county__iexact=selectedCounty)

    if selectedSaletype:
        leads_queryset = leads_queryset.filter(sale_type__iexact=selectedSaletype)

    if psmin:
        leads_queryset = leads_queryset.filter(possible_surplus__gte=psmin)

    if vsmin:
        leads_queryset = leads_queryset.filter(verified_surplus__gte=vsmin)

    if not showHidden == "show":
        leads_queryset = leads_queryset.exclude(hidden_for=user)
    else:
        leads_queryset = leads_queryset.filter(hidden_for=user)



    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 25)
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {
        'current_user':user,
        'leads':leads,
        'total_leads':total_leads,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
        'psmin':psmin,
        'vsmin':vsmin,
        'showHidden':showHidden,

        'second_previous':second_previous
    }
    return render(request, 'Client/available_leads.html', context)

def purchaseLeads(request):
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        lead_count = len(selected_leads_ids)
        
        # Get user credit details
        user_details = UserDetail.objects.get(user=request.user)
        free_credit = user_details.free_credit_balance
        purchased_credit = user_details.purchased_credit_balance

        # Check if user has enough credits
        total_credit = free_credit + purchased_credit
        if lead_count > total_credit:
            messages.error(request, "Insufficient credits to add the selected leads.")
            return redirect('leads')  # Redirect back to the leads page
        else:
            credit_usage = CreditUsage.objects.create(user=request.user)
            # Deduct credits
            remaining_leads = lead_count
            credit_usage.credits_used = remaining_leads
            # Deduct from free credits first
            if free_credit >= remaining_leads:
                user_details.free_credit_balance -= remaining_leads
                credit_usage.number_of_free = remaining_leads
                remaining_leads = 0
                
                messages.info(request, str(lead_count) + ' Credits have been deducted from free credits')
                messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')

            else:
                if free_credit >= 1:

                    remaining_leads -= free_credit
                    credit_usage.number_of_free = free_credit
                    user_details.free_credit_balance = 0
                    # Deduct the rest from purchased credits
                    user_details.purchased_credit_balance -= remaining_leads
                    credit_usage.number_of_purchased = remaining_leads
                    messages.info(request, str(free_credit) + ' free credit and '+str(remaining_leads)+' purchased credit have beed deducted.') 
                    messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')
                else:
                    user_details.purchased_credit_balance -= remaining_leads
                    credit_usage.number_of_purchased = remaining_leads
                    messages.info(request, str(remaining_leads)+' credits deducted from purchased credit balance.') 
                    messages.success(request,str(lead_count) + ' successfully added to My Leads. Visit My Leads Tab to explore lead details.')
            # Save updated credit balances
            user_details.save()
            user_details.update_total_credits()
            credit_usage.save()

            for lead_id in selected_leads_ids:
                status = Status.objects.create(lead_id=lead_id, client=request.user)
                credit_usage.leads.add(status)
                fcl = Foreclosure.objects.get(pk=lead_id)
                fcl.purchased_by.add(request.user)
                
            return redirect('leads')
    else:
        return HttpResponse("Invalid Request", status=400)

def hidefromallLeads(request):
    selectedState = request.POST.get('stateFilter','')
    selectedCounty = request.POST.get('countyFilter','')
    selectedSaletype = request.POST.get('saletypeFilter','')
    psmin = request.POST.get('ps_min','')
    vsmin = request.POST.get('vs_min','')
    unhide = request.POST.get('unhide')
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        if unhide == "show":
            for lead_id in selected_leads_ids:
                unhideLeads = Foreclosure.objects.get(pk=lead_id)
                unhideLeads.hidden_for.remove(request.user)
            messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully unhidden from All Leads! ')
        
        else:
            for lead_id in selected_leads_ids:
                hideLeads = Foreclosure.objects.get(pk=lead_id)
                hideLeads.hidden_for.add(request.user)
            messages.success(request, str(len(selected_leads_ids)) + ' Leads successfully hidden from All Leads! ')
        return redirect('leads')

    else:
        return HttpResponse("Invalid Request", status=400)

def myLeads(request):
    user = request.user
    if request.method == 'POST':
        selectedState = request.POST.get('stateFilter','')
        selectedCounty = request.POST.get('countyFilter','')
        selectedSaletype = request.POST.get('saletypeFilter','')
        psmin = request.POST.get('ps_min','')
        vsmin = request.POST.get('vs_min','')
        showArchived = request.POST.get('show_archived','')

        FAssignment = request.POST.get('assnFilter','')
        SkpStatus = request.POST.get('skpFilter','')
        CallStatus = request.POST.get('callFilter','')
        NegStatus = request.POST.get('negFilter','')
        ClStatus = request.POST.get('clFilter','')
        PdStatus = request.POST.get('pdFilter','')
        AdStatus = request.POST.get('adFilter','')
        LpStatus = request.POST.get('lpFilter','')
    else:
        selectedState = request.GET.get('stateFilter','')
        selectedCounty = request.GET.get('countyFilter','')
        selectedSaletype = request.GET.get('saletypeFilter','')
        psmin = request.GET.get('ps_min','')
        vsmin = request.GET.get('vs_min','')
        showArchived = request.GET.get('show_Archived','')

        FAssignment = request.GET.get('assnFilter','')
        SkpStatus = request.GET.get('skpFilter','')
        CallStatus = request.GET.get('callFilter','')
        NegStatus = request.GET.get('negFilter','')
        ClStatus = request.GET.get('clFilter','')
        PdStatus = request.GET.get('pdFilter','')
        AdStatus = request.GET.get('adFilter','')
        LpStatus = request.GET.get('lpFilter','')


    leads_queryset = Status.objects.filter(client=user)    #.prefetch_related('foreclosure_as_lead')

    states=leads_queryset.values_list("lead__state", flat=True).distinct()

    if not selectedState:
        counties = leads_queryset.values_list("lead__county", flat=True).distinct()
        saletypes = leads_queryset.values_list("lead__sale_type", flat=True).distinct()
    else:
        counties = leads_queryset.filter(lead__state__iexact=selectedState).values_list("lead__county", flat=True).distinct()
        saletypes = leads_queryset.filter(lead__state__iexact=selectedState).values_list("lead__sale_type", flat=True).distinct()
        leads_queryset = leads_queryset.filter(lead__state__iexact=selectedState)
    
    if not showArchived == "show":
        leads_queryset = leads_queryset.filter(archived=False)
    else:
        leads_queryset = leads_queryset.filter(archived=True)

    if selectedCounty:
        leads_queryset = leads_queryset.filter(lead__county__iexact=selectedCounty)

    if selectedSaletype:
        leads_queryset = leads_queryset.filter(lead__sale_type__iexact=selectedSaletype)

    if psmin:
        leads_queryset = leads_queryset.filter(lead__possible_surplus__gte=psmin)

    if vsmin:
        leads_queryset = leads_queryset.filter(lead__verified_surplus__gte=vsmin)



    # Prospecting filter goes here -------------------
    if FAssignment == 'not_assigned':
        leads_queryset = leads_queryset.filter(find_contact_status__in=['not_assigned', ''])
    elif FAssignment:
        leads_queryset = leads_queryset.filter(find_contact_status=FAssignment)
    
    if SkpStatus == 'pending':
        leads_queryset = leads_queryset.filter(skiptracing_status__in =['pending', ''])
    elif SkpStatus:
        leads_queryset = leads_queryset.filter(skiptracing_status = SkpStatus)

    if CallStatus == 'need_to_call':
        leads_queryset = leads_queryset.filter(call_status__in =['need_to_call', ''])
    elif CallStatus:
        leads_queryset = leads_queryset.filter(call_status = CallStatus)
    
    if NegStatus:
        leads_queryset = leads_queryset.filter(negotiation_status = NegStatus)

    if ClStatus:
        leads_queryset = leads_queryset.filter(closing_status = ClStatus)

    if PdStatus:
        leads_queryset = leads_queryset.filter(doc_status = PdStatus)

    if AdStatus:
        leads_queryset = leads_queryset.filter(ag_sent_status = AdStatus)
    
    if LpStatus:
        leads_queryset = leads_queryset.filter(lp_status = LpStatus)
    

    
    total_leads = leads_queryset.count()
    p = Paginator(leads_queryset, 25)
    page = request.GET.get('page')
    leads = p.get_page(page)
    current_page = int(leads.number)
    second_previous = current_page + 2

    context = {
        'current_user':user,
        'leads':leads,
        'total_leads':total_leads,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
        'psmin':psmin,
        'vsmin':vsmin,
        'showArchived':showArchived,
        'FAssignment':FAssignment,
        'SkpStatus':SkpStatus,
        'CallStatus':CallStatus,
        'NegStatus':NegStatus,
        'ClStatus':ClStatus,
        'PdStatus':PdStatus,
        'AdStatus':AdStatus,
        'LpStatus':LpStatus,

        'second_previous':second_previous
    }
    return render(request, 'Client/my_leads.html', context)


def archivefromMyLeads(request):
    showArchived = request.POST.get('show_archived','')
    if request.method == "POST":
        selected_status_ids = request.POST.getlist('selected_items')
        
        for status_id in selected_status_ids:
            statusinstance = Status.objects.get(pk=status_id)
            fclinstance = Foreclosure.objects.get(pk=statusinstance.lead_id)

            if statusinstance.archived == False:
                statusinstance.archived = True
                fclinstance.archived_by.add(request.user)
            elif statusinstance.archived == True:
                statusinstance.archived = False
                fclinstance.archived_by.remove(request.user)
            statusinstance.save()
            
            
        if showArchived == 'show':
            messages.success(request, str(len(selected_status_ids)) + ' Leads unarchived!')
        else:
            messages.success(request, str(len(selected_status_ids)) + ' Leads archived!')
        return redirect('myleads')
    else:
        return HttpResponse("Invalid Request", status=400)

def updateAssignment(request):
    if request.method == "POST":
        assignment_status = request.POST.get('assignment_status')
        selState = request.POST.get('stateFilter','')
        selected_status_ids = request.POST.getlist('selected_items')
        Action = ""
        for status_id in selected_status_ids:
            statusinstance = Status.objects.get(pk=status_id)
            if assignment_status == "not_assigned":
                statusinstance.find_contact_status = "assigned"
                Action = 'Assigned'
            if assignment_status == "assigned":
                statusinstance.find_contact_status = "completed"
                Action = 'Completed'
            if assignment_status == "completed":
                statusinstance.find_contact_status = "verified"
                Action = 'Verified'
            statusinstance.save()
        messages.success(request, str(len(selected_status_ids)) + ' Lead(s) Marked as ' + Action)
        context = {'stateFilter': selState}

        # Encode the dictionary into query parameters
        query_string = urlencode(context)

        # Generate the URL and append the query string
        url = f"{reverse('myleads')}?{query_string}"

        # Redirect to the URL
        return HttpResponseRedirect(url)
        # return HttpResponseRedirect(f"/myleads/?status_id={status_instance.pk}")
        # return redirect('myleads')
    else:
        return HttpResponse("Invalid Request", status=400)


def leadsDetail(request):
    if request.method == "POST":
        selected_status = request.POST.get('status_id')
    else:
        selected_status = request.GET.get('status_id')   
    
    status_instance = Status.objects.get(pk=selected_status)
    if status_instance.client != request.user:
        messages.error(request, "You are not authorized to view this lead.")
        return redirect('myleads')

    alldef = status_instance.lead.defendant.all()
    allplt = status_instance.lead.plaintiff.all()
    alladdress = status_instance.lead.property.all()
    followups = FollowUp.objects.filter(leads=status_instance).order_by('-followup_date')
    Actions = ActionHistory.objects.filter(lead=status_instance).order_by('-created_at')
    CDNotes = Actions.filter(action_source = "Close Deal", action_type = "Note")
    FCNotes = Actions.filter(action_source = "Find Contact", action_type = "Note")
    context = {
        
        'status_instance':status_instance,
        'alldef':alldef,
        'allplt':allplt,
        'alladdress':alladdress,
        'followups':followups,
        'actions':Actions,
        'fcnotes':FCNotes,
        'cdnotes':CDNotes,

        # 'fcl_instance':fcl_instance,
    }
    return render(request, 'Client/leads-detail.html', context)

@csrf_exempt
def saveFDetails(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            followupId = data.get('id')
            notesInput = data.get('notes')
            responseInput = data.get('response')

            
            # Fetch the corresponding event object from the database
            f_instance = FollowUp.objects.get(id=followupId)
            if f_instance:
                f_instance.f_note = notesInput
                f_instance.f_result = responseInput
            f_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})
        except FollowUp.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def updateFstatus(request):
    
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            followupId = data.get('id')
            newStatus = data.get('f_status')
            
            # Fetch the corresponding event object from the database
            f_instance = FollowUp.objects.get(id=followupId)

            if f_instance.f_status == "pending":
                f_instance.f_status = "completed"
            else:
                f_instance.f_status = "pending"
            f_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})
        except FollowUp.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)





def updateContact(request):
    if request.method == "POST":
        selected_status = request.POST.get('status_id')
        assigned_to = request.POST.get('assigned_to','')

        f_c_name = request.POST.get('f_c_name','')
        f_c_email = request.POST.get('f_c_email','')
        f_c_phone = request.POST.get('f_c_phone','')
        f_c_address = request.POST.get('f_c_address','')
        f_c_notes = request.POST.get('f_c_notes','')
        s_c_name = request.POST.get('s_c_name','')
        s_c_email = request.POST.get('s_c_email','')
        s_c_phone = request.POST.get('s_c_phone','')
        s_c_address = request.POST.get('s_c_address','')
        s_c_notes = request.POST.get('s_c_notes','')
        find_contact_comment = request.POST.get('find_contact_comment','')
        find_contact_status= request.POST.get('find_contact_status','')
    
    else:
        selected_status = request.GET.get('status_id')

        f_c_name = request.GET.get('f_c_name','')
        f_c_email = request.GET.get('f_c_email','')
        f_c_phone = request.GET.get('f_c_phone','')
        f_c_address = request.GET.get('f_c_address','')
        f_c_notes = request.GET.get('f_c_notes','')
        s_c_name = request.GET.get('s_c_name','')
        s_c_email = request.GET.get('s_c_email','')
        s_c_phone = request.GET.get('s_c_phone','')
        s_c_address = request.GET.get('s_c_address','')
        s_c_notes = request.GET.get('s_c_notes','')
        find_contact_comment = request.GET.get('find_contact_comment','')
        find_contact_status = request.GET.get('find_contact_status','')
    
    status_instance = Status.objects.get(pk=selected_status)
#    numberinuse = request.POST.get('numberinuse','')
    if f_c_name:
        status_instance.first_contact_name = f_c_name
    if f_c_email:
        status_instance.first_contact_email = f_c_email
    if f_c_phone:
        status_instance.first_contact_phone = f_c_phone
    if f_c_address:
        status_instance.first_contact_address = f_c_address
    if f_c_notes:
        status_instance.first_contact_comment = f_c_notes
    if s_c_name:
        status_instance.second_contact_name = s_c_name
    if s_c_email:
        status_instance.second_contact_email = s_c_email
    if s_c_phone:
        status_instance.second_contact_phone = s_c_phone
    if s_c_address:
        status_instance.second_contact_address = s_c_address
    if s_c_notes:
        status_instance.second_contact_comment = s_c_notes
    if find_contact_comment:
        status_instance.find_contact_notes = find_contact_comment
    if find_contact_status:
        status_instance.find_contact_status = find_contact_status

#    status_instance.number_in_use = numberinuse
    status_instance.save()
    

    return HttpResponseRedirect(f"/leads-detail/?status_id={status_instance.pk}")


@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def updateArchived(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            StatusID = data.get('Status_id')
            
            # Fetch the corresponding event object from the database
            status_instance = Status.objects.get(id=StatusID)

            if status_instance.archived == True:
                status_instance.archived = False
            else:
                status_instance.archived = True
            status_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})
        except Status.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def createFollowup(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            StatusID = data.get('status_id')
            FDate= data.get('f_date')
            FTask = data.get('f_task')
            user = request.user
            # Fetch the corresponding event object from the database
            status_instance = Status.objects.get(id=StatusID)

            # Check if the field exists in the model
            if status_instance:
                Fcreate = FollowUp.objects.create(
                    client = user,
                    leads = status_instance,
                    followup_date = FDate,
                    f_note = FTask,
                    f_status = "pending"
                )
                Fcreate.save()
     
            # status_instance.StatusFor = SelectedStatus

            # status_instance.save()
           # Respond with success
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!', 'new_id': Fcreate.id})

        except FollowUp.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)






@csrf_exempt
def updateStatus_ajax(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            StatusID = data.get('Status_id')
            SelectedStatus = data.get('selected_status')
            StatusFor = data.get('status_for')
            Section = data.get('ActionSection')
            # Fetch the corresponding event object from the database
            status_instance = Status.objects.get(id=StatusID)

            # Check if the field exists in the model
            if hasattr(status_instance, StatusFor):
                # Dynamically set the value for the field
                setattr(status_instance, StatusFor, SelectedStatus)
                
                status_instance.save()
            # related field actions----------
            if SelectedStatus == 're_skiptrace':
                status_instance.find_contact_status = "assigned"
                status_instance.save()
            Action = ""
            if SelectedStatus:
                Action = SelectedStatus
            FAction = STATUS_MAPPING.get(Action, Action)
            user=request.user
            Timeline_instance = ActionHistory.objects.create(
                client = user,
                lead = status_instance,
                action_source = Section, #add action source dynamically
                action_type = "Status",
                action = FAction,
                details = "",
            )
            Timeline_instance.save()


            # status_instance.StatusFor = SelectedStatus

            # status_instance.save()
           # Respond with success
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Status.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def UpdateText(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            StatusID = data.get('Status_id')
            StatusFor = data.get('status_for')
            TextValue = data.get('Text')
            Name = data.get('Action')
            Section = data.get('section')
        
            # Fetch the corresponding event object from the database
            status_instance = Status.objects.get(id=StatusID)

            # Check if the field exists in the model
            if hasattr(status_instance, StatusFor):
                # Dynamically set the value for the field
                setattr(status_instance, StatusFor, TextValue)
                status_instance.save()
            
            Timeline_instance = ActionHistory.objects.create(
                client = request.user,
                lead = status_instance,
                action_source = Section, #add action source dynamically
                action_type = "Text",
                action = Name,
                details = TextValue,
            )
            Timeline_instance.save()


            # status_instance.StatusFor = SelectedStatus

            # status_instance.save()
           # Respond with success
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Status.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



def export_data(request):
    data = set()
    if request.method == "POST":
        selected_leads_ids = request.POST.getlist('selected_items')
        for lead in selected_leads_ids:
            data.add(Foreclosure.objects.get(pk=lead))

    # data = Foreclosure.objects.filter(surplus_status="Fund Available").prefetch_related('defendant__wireless', 'defendant__landline', 'defendant__emails')
    resources = ClientModelResource()
    dataset = resources.export(data)
    response = HttpResponse(dataset.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response

def exportMyleads(request):
    data = set()
    if request.method == "POST":
        selected_status_ids = request.POST.getlist('selected_items')
        for status in selected_status_ids:
            status_instance = Status.objects.get(pk=status)
            data.add(status_instance.lead)

    # data = Foreclosure.objects.filter(surplus_status="Fund Available").prefetch_related('defendant__wireless', 'defendant__landline', 'defendant__emails')
    resources = ClientModelResource()
    dataset = resources.export(data)
    response = HttpResponse(dataset.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response

@csrf_exempt
def update_CLStatus(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            StatusID = data.get('status_id')
            selectedValue = data.get('status')

            # Fetch the corresponding event object from the database
            status_instance = Status.objects.get(id=StatusID)

            # Check if the field exists in the model
            if status_instance:
                # Dynamically set the value for the field
                status_instance.closing_status = selectedValue
                status_instance.save()
            Action = ""
            if selectedValue:
                Action = selectedValue
            FAction = STATUS_MAPPING.get(Action, Action)
            Timeline_instance = ActionHistory.objects.create(
            client = request.user,
            lead = status_instance,
            action_source = "Close Deal",
            action_type = "Status",
            action = FAction,
            details = "",
            )
            Timeline_instance.save()
        
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Status.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Status not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)




def CloseDealNote(request):
    if request.method == "POST":
        selected_status = request.POST.get('SID')
        status_instance = Status.objects.get(pk=selected_status)
        CD_note = request.POST.get('CD_note')

        PDoc_Status = request.POST.get('PDoc_Status')
        AGSent_Status = request.POST.get('AGSent_Status')
        LP_Status = request.POST.get('LP_Status')
        CC_NotFunded = request.POST.get('CC_NotFunded')
        Action = ""
        if PDoc_Status:
            Action = PDoc_Status
        elif AGSent_Status:
            Action = AGSent_Status
        elif LP_Status:
            Action = LP_Status
        elif CC_NotFunded:
            Action = CC_NotFunded
        FAction = STATUS_MAPPING.get(Action, Action)
        Timeline_instance = ActionHistory.objects.create(
            client = request.user,
            lead = status_instance,
            action_source = "Close Deal",
            action_type = "Note",
            action = FAction,
            details = CD_note,
            )
        Timeline_instance.save()
        messages.success(request, "Notes Added.")

    return HttpResponseRedirect(f"/leads-detail/?status_id={status_instance.pk}")

from decimal import Decimal
def updatedClosed(request):
    if request.method == 'POST':
        selected_status = request.POST.get('StatusID')
        disbursed = request.POST.get('disbursed')
        f_share = request.POST.get('f_share')
        a_cost = request.POST.get('a_cost')
        o_cost = request.POST.get('o_cost')



        status_instance = Status.objects.get(pk=selected_status)
        if disbursed:
            status_instance.total_disbursed = Decimal(disbursed)
        if f_share:
            status_instance.fee_agreement_share = Decimal(f_share)
        if a_cost:
            status_instance.attorney_cost = Decimal(a_cost)
        if o_cost:
            status_instance.other_costs = Decimal(o_cost)
        status_instance.update_net_profit()
        status_instance.save()
        messages.success(request, 'Accounting Updated')
    return HttpResponseRedirect(f"/leads-detail/?status_id={status_instance.pk}")

@csrf_exempt
def delete_action(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
          
            actionID = data.get('action_id')           
            action = ActionHistory.objects.get(pk=actionID)  # Replace `Action` with your model name
            action.delete()
            return JsonResponse({'status': 'success'})
        except ActionHistory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Action not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
