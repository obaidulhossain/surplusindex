from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect, HttpResponse

from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse


from django.contrib import messages
from datetime import timedelta

# -----------Forms------------------
from django.forms import modelformset_factory
from .forms import *
from propertydata.forms import *
# -----------Models------------------
from . models import *
from realestate_directory.models import *
from propertydata.models import *
# -----------Resources---------------
from .resources import *

imported_data_cache = None

# Create your views here.
def EventsCalendar(request):
    current_user=request.user

    all_states = foreclosure_Events.objects.values_list('state', flat=True).distinct()
    # Get the filter option from the query parameters
    filter_option = request.GET.get('filter', 'all')
    state_selected = request.GET.get('states', 'All')
    selected_sale_types = request.GET.getlist('sale_type')


    option1 = ""
    option2 = ""
    option3 = ""
    option4 = ""
    saletypetax = False
    saletypemtg = False
    saletypeoth = False

    if 'Tax' in selected_sale_types:
        saletypetax = True
    
    if 'Mtg' in selected_sale_types:
        saletypemtg = True

    if 'Oth' in selected_sale_types:
        saletypeoth = True
    
    saletype_selected = []
    if saletypetax:
        saletype_selected.append('Tax')
    if saletypemtg:
        saletype_selected.append('Mortgage')
    if saletypeoth:
        saletype_selected.append('Others')
    # Determine the queryset based on the filter option
    
    if filter_option == 'past':
        if state_selected == 'All' or state_selected == '':
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), sale_type__in=saletype_selected, assigned_to=current_user)
                option2="selected"
                option4 = 'All'
            else:
                events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), assigned_to=current_user)
                option2="selected"
                option4 = 'All'
        else:
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), state=state_selected, sale_type__in=saletype_selected, assigned_to=current_user)
                option2="selected"
                option4=state_selected
            else:
                events_queryset = foreclosure_Events.objects.filter(event_next__lt=now().date(), state=state_selected, assigned_to=current_user)
                option2="selected"
                option4=state_selected
    elif filter_option == 'upcoming':
        if state_selected == 'All' or state_selected == '':
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), sale_type__in=saletype_selected, assigned_to=current_user)
                option3="selected"
                option4='All'
            else:    
                events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), assigned_to=current_user)
                option3="selected"
                option4='All'
        else:
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), state=state_selected, sale_type__in=saletype_selected, assigned_to=current_user)
                option3="selected"
                option4=state_selected
            else:    
                events_queryset = foreclosure_Events.objects.filter(event_next__gte=now().date(), state=state_selected, assigned_to=current_user)
                option3="selected"
                option4=state_selected
    else:  # Default to 'all'
        if state_selected == 'All' or state_selected == '':
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(sale_type__in=saletype_selected, assigned_to=current_user)
                option1="selected"
                option4='All'                
            else:
                events_queryset = foreclosure_Events.objects.filter(assigned_to=current_user)
                option1="selected"
                option4='All'
        else:
            if saletype_selected:
                events_queryset = foreclosure_Events.objects.filter(state=state_selected, sale_type__in=saletype_selected, assigned_to=current_user)
                option1="selected"
                option4=state_selected    
            else:
                events_queryset = foreclosure_Events.objects.filter(state=state_selected, assigned_to=current_user)
                option1="selected"
                option4=state_selected




    
    # Paginate the results
    p = Paginator(events_queryset, 15)
    page = request.GET.get('page')
    events = p.get_page(page)


    current_page = int(events.number)
    second_previous = current_page + 2

    context = {
        'events':events,
        'all_states':all_states,
        'second_previous':second_previous,
        'filter_option':filter_option, # Pass the current filter option to the template
        'option1':option1,
        'option2':option2,
        'option3':option3,
        'option4':option4,
        'selected_sale_types':selected_sale_types,
        'saletypetax':saletypetax,
        'saletypemtg':saletypemtg,
        'saletypeoth':saletypeoth,
        'current_user':current_user
    }
    return render(request, 'da/events_calendar.html', context)

def ActiveTasks(request):
    current_user=request.user
    p=Paginator(Foreclosure.objects.filter(case_search_assigned_to=current_user, changed_at__lt=now().date() - timedelta(days=7)) | Foreclosure.objects.filter(case_search_assigned_to=current_user, case_search_status="Pending"), 20)
    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    counties=Foreclosure.objects.values_list("county", flat=True).distinct()
    saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()
    page = request.GET.get('page')
    checklist = p.get_page(page)
    current_page = int(checklist.number)
    second_previous = current_page + 2
    

    context = {
        'current_user':current_user,
        'checklist':checklist,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'second_previous':second_previous
        }
    return render(request,'da/active_tasks.html',context)

def skiptrace(request):
    researcher = request.user.groups.filter(name="researcher").exists()
    all_contact = Contact.objects.all().distinct()
    
    if request.method == 'POST':
        contact_selected = request.POST.get('con_id','')
    else:
        contact_selected = request.GET.get('con_id','')
    if contact_selected:
        current_con_instance = get_object_or_404(Contact, pk=contact_selected)
        all_mailing = current_con_instance.mailing_address.all()
        all_email = current_con_instance.emails.all()
        all_wireless = current_con_instance.wireless.all()
        all_landline = current_con_instance.landline.all()
    else:
        current_con_instance = None
        all_mailing = None
        all_email = None
        all_wireless = None
        all_landline = None

    
    context = {
        'all_contact':all_contact,
        'contact_selected':contact_selected,
        'current_con_instance':current_con_instance,
        'all_mailing':all_mailing,
        'all_email':all_email,
        'all_wireless':all_wireless,
        'all_landline':all_landline,
        'researcher':researcher,
    }
    return render(request,'projects/skiptrace.html', context)

#Email Section -----------------------------------------------------------------------Start
def update_email(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        email = request.POST.get('email_id')
        if email:
            emailinstance = Email.objects.get(pk=email)
            emailinstance.email_address = request.POST.get('email')
            emailinstance.save()
            messages.info(request, "Email Saved!")
    return HttpResponseRedirect(f"/skiptrace/?con_id={contact}#em")

def search_create_email(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        emailaddress = request.POST.get('email')
        createEmail = Email(email_address = emailaddress)
        createEmail.save()
        messages.success(request,'New Email Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.emails.add(createEmail)
            messages.info(request, 'Email added to current contact instance')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#em")

def filterEmail(request):
    emailaddress = request.GET.get('email')
    emails = Email.objects.all()
    if emailaddress:
        emails = emails.filter(email_address__icontains=emailaddress)
    results = list(emails.values('id', 'email_address'))
    return JsonResponse({'emails':results})

def add_email(request):
    selected_contact = request.POST.get('con_id')
    emailid = request.POST.get('email_id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        emailinstance = Email.objects.get(pk=emailid)
        contactinstance.emails.add(emailinstance)
        messages.info(request,'Email added to contact')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#em")
#Email Section -----------------------------------------------------------------------End

#Wireless Section -----------------------------------------------------------------------Start
def update_wireless(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        wireless = request.POST.get('wireless-id')
        if wireless:
            w_instance = Wireless_Number.objects.get(pk=wireless)
            w_instance.w_number = request.POST.get('wireless')
            w_instance.save()
            messages.info(request, "Number Updated!")
    return HttpResponseRedirect(f"/skiptrace/?con_id={contact}#wn")

def create_wireless(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        wNumber = request.POST.get('wireless')
        createwireless = Wireless_Number(w_number = wNumber)
        createwireless.save()
        messages.success(request,'New Wireless Number Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.wireless.add(createwireless)
            messages.info(request, 'Wireless Number added to current contact instance')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#wn")

def filterWireless(request):
    w_number = request.GET.get('wireless')
    wireless = Wireless_Number.objects.all()
    if w_number:
        wireless = wireless.filter(w_number__icontains=w_number)
    results = list(wireless.values('id', 'w_number'))
    return JsonResponse({'wireless':results})

def add_wireless(request):
    selected_contact = request.POST.get('con_id')
    w_id = request.POST.get('wireless-id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        w_instance = Wireless_Number.objects.get(pk=w_id)
        contactinstance.wireless.add(w_instance)
        messages.info(request,'Wireless number added to contact')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#wn")
#Wireless Section -----------------------------------------------------------------------End

#landline Section -----------------------------------------------------------------------Start
def updateLandline(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        landline = request.POST.get('landline-id')
        if landline:
            l_instance = Landline_Number.objects.get(pk=landline)
            l_instance.l_number = request.POST.get('landline')
            l_instance.save()
            messages.info(request, "Landline Number Updated!")
    return HttpResponseRedirect(f"/skiptrace/?con_id={contact}#ln")

def createLandline(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        lNumber = request.POST.get('landline')
        createlandline = Landline_Number(l_number = lNumber)
        createlandline.save()
        messages.success(request,'New Landline Number Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.landline.add(createlandline)
            messages.info(request, 'Landline Number added to current contact instance')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#ln")

def filterLandline(request):
    l_number = request.GET.get('landline')
    landline = Landline_Number.objects.all()
    if l_number:
        landline = landline.filter(l_number__icontains=l_number)
    results = list(landline.values('id', 'l_number'))
    return JsonResponse({'landline':results})

def addLandline(request):
    selected_contact = request.POST.get('con_id')
    l_id = request.POST.get('landline-id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        l_instance = Landline_Number.objects.get(pk=l_id)
        contactinstance.landline.add(l_instance)
        messages.info(request,'Landline number added to contact')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contactinstance.pk}#ln")
#landline Section -----------------------------------------------------------------------End

#Mailing Address Section -----------------------------------------------------------------------Start
def fetch_mailing_address(request):
    selected_contact = request.POST.get('con_id')
    contact_instance = Contact.objects.get(pk=selected_contact)
    foreclosures = Foreclosure.objects.filter(defendant=contact_instance)
    for fcl in foreclosures:
        properties = fcl.property.all()
        for prop in properties:
            property_instance = Property.objects.get(pk=prop.pk)
            contact_instance.mailing_address.add(property_instance)
    messages.info(request, 'Successfully Fetched All Mailing Addresses')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contact_instance.pk}#mailing_address")

    
    
    
    
    pass

def addMailing(request):
    if request.method == 'POST':
        update = request.POST.get('con_id')
        add_prop = request.POST.get('property_id')
        coninstance = Contact.objects.get(pk=update)
        propinstance = Property.objects.get(pk=add_prop)
        coninstance.mailing_address.add(propinstance)
        messages.success(request,'Mailing Address successfully added to current contact')

    #return HttpResponseRedirect(f"/foreclosures/?g_caseid={selected}")
    return HttpResponseRedirect(f"/skiptrace/?con_id={update}")
#Mailing Address Section -----------------------------------------------------------------------End

def CreateUpdateContact(request):
    current_user = request.user        #.groups.filter(name="researcher").exists()
    contact_selected = request.POST.get('con_id','')
    prefix = request.POST.get('prefix','')
    f_name = request.POST.get('f_name','')
    m_name = request.POST.get('m_name','')
    l_name = request.POST.get('l_name','')
    suffix = request.POST.get('suffix', '')
    b_name = request.POST.get('b_name','')
    designation = request.POST.get('designation','')

    if contact_selected:
        contact_instance = Contact.objects.get(pk=contact_selected)
        contact_instance.name_prefix = prefix
        contact_instance.first_name = f_name
        contact_instance.middle_name = m_name
        contact_instance.last_name = l_name
        contact_instance.name_suffix = suffix
        contact_instance.business_name = b_name
        contact_instance.designation = designation
    else:
        contact_instance = Contact(
            name_prefix = prefix,
            first_name = f_name,
            middle_name = m_name,
            last_name = l_name,
            name_suffix = suffix,
            business_name = b_name,
            designation = designation,
            )
        
    contact_instance.save()
    if contact_selected:
        messages.success(request, 'Contact Instance Updated Successfully!!')
    else:
        messages.success(request, 'New Contact Instance Created!!')
    contact_selected = contact_instance.pk

    # return redirect('add_edit_fcl')
    return HttpResponseRedirect(f"/skiptrace/?con_id={contact_selected}")

def filter_contact(request):
        prefix = request.GET.get('prefix','')
        firstname = request.GET.get('f_name','')
        middlename = request.GET.get('m_name','')
        lastname = request.GET.get('l_name','')
        suffix = request.GET.get('suffix','')
        business = request.GET.get('business','')
        
#stop here if needed 
        # Query the database using Q objects
        contact = Contact.objects.all()
        if prefix:
            contact = contact.filter(name_prefix__icontains=prefix)
        if firstname:
            contact = contact.filter(first_name__icontains=firstname)
        if middlename:
            contact = contact.filter(middle_name__icontains=middlename)
        if lastname:
            contact = contact.filter(last_name__icontains=lastname)
        if suffix:
            contact = contact.filter(name_suffix__icontains=suffix)
        if business:
            contact = contact.filter(business_name__icontains=business)
        results = []
        for con in contact:
            mailing_addresses = []
            for prop in con.mailing_address.all():
                mailing_addresses.append(f"{prop.house_number} {prop.road_name} {prop.road_type} {prop.direction} {prop.apt_unit} {prop.extention}, {prop.city} {prop.zip_code}")
            results.append({
                'id': con.id,
                'name_prefix': con.name_prefix,
                'first_name': con.first_name,
                'middle_name': con.middle_name,
                'last_name': con.last_name,
                'name_suffix': con.name_suffix,
                'business_name': con.business_name,
                'mailing_addresses': mailing_addresses,
            })
        # Return results as JSON
        #results = list(contact.values('id', 'name_prefix', 'first_name', 'middle_name', 'last_name', 'name_suffix', 'business_name'))
        return JsonResponse({'contact': results})

def update_contact(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id')
        property = request.POST.get('propid')
        parcel = request.POST.get('parcel')
        state = request.POST.get('state')
        county = request.POST.get('county')
        house = request.POST.get('house')
        road = request.POST.get('road')
        roadtype = request.POST.get('type')
        dir = request.POST.get('dir')
        apt = request.POST.get('apt')
        ext = request.POST.get('ext')
        city = request.POST.get('city')
        zip = request.POST.get('zip')
        if property:
            property_instance = get_object_or_404(Property, pk=property)
            property_instance.parcel = parcel
            property_instance.state = state
            property_instance.county = county
            property_instance.house_number = house
            property_instance.road_name = road
            property_instance.road_type = roadtype
            property_instance.direction = dir
            property_instance.apt_unit = apt
            property_instance.extention = ext
            property_instance.city = city
            property_instance.zip_code = zip
            property_instance.save()
            messages.success(request, 'Property Record Saved')

    return HttpResponseRedirect(f"/skiptrace/?con_id={contact}")

def assign_skp(request):
    current_user=request.user
    p=Paginator(Contact.objects.filter(skp_assignedto=current_user, skiptraced=False), 20)
    states=Foreclosure.objects.values_list("state", flat=True).distinct()
    counties=Foreclosure.objects.values_list("county", flat=True).distinct()
    saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()
    page = request.GET.get('page')
    checklist = p.get_page(page)
    current_page = int(checklist.number)
    second_previous = current_page + 2
    

    context = {
        'current_user':current_user,
        'checklist':checklist,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'second_previous':second_previous
        }
    return render(request,'da/active_skp.html',context)

def deliveredtasks(request):
    current_user=request.user
    p=Paginator(Foreclosure.objects.filter(case_search_assigned_to=current_user, case_search_status = "Completed"), 20)
    # states=Foreclosure.objects.values_list("state", flat=True).distinct()
    # counties=Foreclosure.objects.values_list("county", flat=True).distinct()
    # saletypes=Foreclosure.objects.values_list("sale_type", flat=True).distinct()
    page = request.GET.get('page')
    deliveredlist = p.get_page(page)
    current_page = int(deliveredlist.number)
    second_previous = current_page + 2
    context = {
        'deliveredlist':deliveredlist,
        'current_page':current_page,
        'second_previous':second_previous,


    }
    return render(request,'da/delivered_tasks.html',context)

#--------------Foreclosure views------------------------

def fclview(request):
    researcher = request.user.groups.filter(name="researcher").exists()
    
    all_foreclosure = Foreclosure.objects.all().distinct()
    if request.method == 'POST':
        selected_foreclosure = request.POST.get('caseid','')
    else:
        selected_foreclosure = request.GET.get('fcl_id','')
    if selected_foreclosure:
        current_fcl_instance = get_object_or_404(Foreclosure, pk=selected_foreclosure)
        all_prop = current_fcl_instance.property.all()
        all_plt = current_fcl_instance.plaintiff.all()
        all_def = current_fcl_instance.defendant.all()
    else:
        current_fcl_instance = None
        all_prop = None
        all_plt = None
        all_def = None    

    
    context = {
        'all_foreclosure':all_foreclosure,
        'selected_foreclosure':selected_foreclosure,
        'current_fcl_instance':current_fcl_instance,
        'all_prop':all_prop,
        'all_plt':all_plt,
        'all_def':all_def,
        'researcher':researcher,
    }
    return render(request, 'projects/add_edit_foreclosure.html', context)

def filter_foreclosure(request):
    state = request.GET.get('f_state','')
    county = request.GET.get('f_county','')
    case_num = request.GET.get('case_num','')
    sale_type = request.GET.get('sale_type','')
    sale_status = request.GET.get('sale_status','')
    

    # Query the database using Q objects
    foreclosure = Foreclosure.objects.all()
    if state:
        foreclosure = foreclosure.filter(state__icontains=state)
    if county:
        foreclosure = foreclosure.filter(county__icontains=county)
    if case_num:
        foreclosure = foreclosure.filter(case_number__icontains=case_num)
    if sale_type:
        foreclosure = foreclosure.filter(sale_type__icontains=sale_type)
    if sale_status:
        foreclosure = foreclosure.filter(sale_status__icontains=sale_status)

    # Return results as JSON
    results = list(foreclosure.values('id', 'state', 'county', 'case_number', 'sale_date', 'sale_type', 'sale_status'))
    return JsonResponse({'foreclosure': results})

def update_foreclosure(request):
    current_user = request.user        #.groups.filter(name="researcher").exists()
    sel_fcl = request.POST.get('caseid','')
    
    case = request.POST.get('case_num','')
    county = request.POST.get('f_county','')
    state = request.POST.get('f_state','')
    sale_date = request.POST.get('sale_date', '')
    sale_type = request.POST.get('sale_type','')
    sale_status = request.POST.get('sale_status','')

    judgment = request.POST.get('judgment', '')
    saleprice = request.POST.get('saleprice', '')
    possible_sf = request.POST.get('possible_sf', '')
    verified_sf = request.POST.get('verified_sf', '')
    surplus_status = request.POST.get('surplus_status', '')

    case_ext = request.POST.get('case_ext','')
    court_name = request.POST.get('court_name','')
    case_type = request.POST.get('case_type','')
    case_status = request.POST.get('case_status','')
    case_search_status = request.POST.get('case_search_status','')
    
    
    if sel_fcl:
        fcl_instance = Foreclosure.objects.get(pk=sel_fcl)
        
        fcl_instance.case_number = case
        fcl_instance.county = county
        fcl_instance.state = state
        if not sale_date == "":
            fcl_instance.sale_date = sale_date
        fcl_instance.sale_type = sale_type
        fcl_instance.sale_status = sale_status
        
        if not judgment == "":
            fcl_instance.fcl_final_judgment = judgment
        if not saleprice == "":
            fcl_instance.sale_price = saleprice
        if not possible_sf == "":
            fcl_instance.possible_surplus = possible_sf
        if not verified_sf == "":
            fcl_instance.verified_surplus = verified_sf
        fcl_instance.surplus_status = surplus_status
        
        fcl_instance.case_number_ext = case_ext
        fcl_instance.court_name = court_name
        fcl_instance.case_type = case_type
        fcl_instance.case_status = case_status
        if current_user.groups.filter(name="researcher").exists() and case_search_status == "Verified":
            fcl_instance.case_search_status = "Completed"
        else:
            fcl_instance.case_search_status = case_search_status
    
    else:
        fcl_instance = Foreclosure(
            state=state,
            county=county,
            case_number=case,
            sale_type=sale_type,
            sale_status=sale_status,
            case_search_status="Pending"
            # case_number_ext=case_ext,
            # court_name=court_name,
            # case_type=case_type,
            # case_status=case_status,
            # sale_date=sale_date,

            # fcl_final_judgment=judgment,
            # sale_price=saleprice,
            # possible_surplus=possible_sf,
            # verified_surplus=verified_sf,
            # surplus_status=surplus_status,
            )
        
    fcl_instance.save()
    if sel_fcl:
        messages.success(request, 'Foreclosure Instance Updated Successfully!!')
    else:
        messages.success(request, 'New Foreclosure Instance Created!!')
    sel_fcl = fcl_instance.pk

    # return redirect('add_edit_fcl')
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={sel_fcl}")

#---------------foreclosureview-----------------end

#--------------defendant Section----------------Start
def add_defendant(request):
   if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        defendant = request.POST.get('defid')
        def_instance = get_object_or_404(Contact, pk=defendant)
        fcl_instance = get_object_or_404(Foreclosure, pk=foreclosure)
        fcl_instance.defendant.add(def_instance)
        messages.success(request, "Defendant Added to Foreclosure Instance!")
        return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#def")

def defendant_search(request):

    prefix = request.GET.get('prefix', '')
    first = request.GET.get('first', '')
    middle = request.GET.get('middle', '')
    last = request.GET.get('last', '')
    suffix = request.GET.get('suffix', '')
    business = request.GET.get('business', '')
    designation = request.GET.get('designation', '')
    
    
    # Query the database using Q objects
    defendant = Contact.objects.all()
    if prefix:
        defendant = defendant.filter(name_prefix__icontains=prefix)
    if first:
        defendant = defendant.filter(first_name__icontains=first)
    if middle:
        defendant = defendant.filter(middle_name__icontains=middle)
    if last:
        defendant = defendant.filter(last_name__icontains=last)
    if suffix:
        defendant = defendant.filter(name_suffix__icontains=suffix)
    if business:
        defendant = defendant.filter(business_name__icontains=business)
    if designation:
        defendant = defendant.filter(designation__icontains=designation)
    
    # Return results as JSON
    defresults = list(defendant.values('id', 'name_prefix', 'first_name', 'middle_name', 'last_name', 'name_suffix', 'business_name', 'designation'))
    return JsonResponse({'defendant': defresults})

def search_create_defendant(request):
    if request.method == 'POST':

        foreclosure = request.POST.get('caseid')
        prefix = request.POST.get('prefix')
        first = request.POST.get('first')
        middle = request.POST.get('middle')
        last = request.POST.get('last')
        suffix = request.POST.get('suffix')
        business = request.POST.get('business')
        designation = request.POST.get('designation')

        add_defendant = Contact(name_prefix=prefix, first_name=first, middle_name=middle, last_name=last, name_suffix=suffix, business_name=business, designation=designation)
        add_defendant.save()
        messages.success(request, 'Defendant Record Created')
        if foreclosure:
            fcl_instance = get_object_or_404(Foreclosure, pk=foreclosure)
            fcl_instance.defendant.add(add_defendant)
            messages.info(request, 'Defendant Added to Current Foreclosure Instance')
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#def")

def update_defendant(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        defendant = request.POST.get('def-id')
        prefix = request.POST.get('u_prefix')
        first = request.POST.get('u_first')
        middle = request.POST.get('u_middle')
        last = request.POST.get('u_last')
        suffix = request.POST.get('u_suffix')
        business = request.POST.get('u_business_name')
        designation = request.POST.get('u_designation')




        def_instance = get_object_or_404(Contact,pk=defendant)
        def_instance.name_prefix = prefix
        def_instance.first_name = first
        def_instance.middle_name = middle
        def_instance.last_name = last
        def_instance.name_suffix = suffix
        def_instance.business_name = business
        def_instance.designation = designation
        def_instance.save()
        messages.success(request, "Defendant Updated Successfully!")
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#def")
#--------------defendant Section----------------end

#--------------Plaintiff Section----------------Start
def create_update_plaintiff(request):
    if request.method == 'POST':

        foreclosure = request.POST.get('caseid')
        # property = request.POST.get('propertyid')
        contact_nm = request.POST.get('contact_name')
        business_nm = request.POST.get('business_name')
        dba = request.POST.get('dba')
        add_plaintiff = ForeclosingEntity(individual_name=contact_nm, business_name=business_nm, dba=dba)
        add_plaintiff.save()
        messages.success(request, 'Foreclosing Entity Record Created')
        if foreclosure:
            fcl_instance = get_object_or_404(Foreclosure, pk=foreclosure)
            fcl_instance.plaintiff.add(add_plaintiff)
            messages.info(request, 'Foreclosing Entity Added to Current Foreclosure Instance')
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#plt")

def update_plaintiff(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        # property = request.POST.get('propertyid')
        plaintiff = request.POST.get('plt-id')
        contact_nm = request.POST.get('u_contact')
        business_nm = request.POST.get('u_business')
        dba = request.POST.get('u_dba')
        plt_instance = get_object_or_404(ForeclosingEntity,pk=plaintiff)
        plt_instance.individual_name = contact_nm
        plt_instance.business_name = business_nm
        plt_instance.dba = dba
        plt_instance.save()
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#plt")

def add_plaintiff(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        # property = request.POST.get('propertyid')
        plaintiff = request.POST.get('pltid')
        plt_instance = get_object_or_404(ForeclosingEntity, pk=plaintiff)
        fcl_instance = get_object_or_404(Foreclosure, pk=foreclosure)
        fcl_instance.plaintiff.add(plt_instance)
        messages.success(request, "Plaintiff Added to Foreclosure Instance")
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#plt")

def plaintiff_search(request):
    business = request.GET.get('business_name', '')
    dba = request.GET.get('dba', '')
    contact = request.GET.get('contact_name', '')
    
    # Query the database using Q objects
    plaintiff = ForeclosingEntity.objects.all()
    if business:
        plaintiff = plaintiff.filter(business_name__icontains=business)
    if dba:
        plaintiff = plaintiff.filter(dba__icontains=dba)
    if contact:
        plaintiff = plaintiff.filter(individual_name__icontains=contact)
    
    # Return results as JSON
    pltresults = list(plaintiff.values('id','business_name', 'dba','individual_name'))
    return JsonResponse({'plaintiff': pltresults})
#--------------Plaintiff Section----------------End

#------------------property-------------Start
def search_create_property(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        contact = request.POST.get('con_id')
        parcel = request.POST.get('parcel')
        state = request.POST.get('state')
        county = request.POST.get('county')
        house = request.POST.get('house')
        road = request.POST.get('road')
        roadtype = request.POST.get('type')
        dir = request.POST.get('dir')
        apt = request.POST.get('apt')
        ext = request.POST.get('ext')
        city = request.POST.get('city')
        zip = request.POST.get('zip')
        add_property = Property(parcel=parcel, state=state, county=county, house_number=house, road_name=road, road_type=roadtype, direction=dir, apt_unit=apt, extention=ext, city=city, zip_code=zip)
        add_property.save()
        messages.success(request, 'Property Record Created')
    if foreclosure:
        foreclosure = Foreclosure.objects.get(pk=foreclosure)
        foreclosure.property.add(add_property)
        messages.info(request, 'Property Added to Current Foreclosure Instance')
        return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure.pk}#prop")
    elif contact:
        contact = Contact.objects.get(pk=contact)
        contact.mailing_address.add(add_property)
        messages.info(request, 'Contact Added to Current Foreclosure Instance')
        return HttpResponseRedirect(f"/skiptrace/?con_id={contact.pk}")

def update_property(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        property = request.POST.get('propid')
        parcel = request.POST.get('parcel')
        state = request.POST.get('state')
        county = request.POST.get('county')
        house = request.POST.get('house')
        road = request.POST.get('road')
        roadtype = request.POST.get('type')
        dir = request.POST.get('dir')
        apt = request.POST.get('apt')
        ext = request.POST.get('ext')
        city = request.POST.get('city')
        zip = request.POST.get('zip')
        if property:
            property_instance = get_object_or_404(Property, pk=property)
            property_instance.parcel = parcel
            property_instance.state = state
            property_instance.county = county
            property_instance.house_number = house
            property_instance.road_name = road
            property_instance.road_type = roadtype
            property_instance.direction = dir
            property_instance.apt_unit = apt
            property_instance.extention = ext
            property_instance.city = city
            property_instance.zip_code = zip
            property_instance.save()
            messages.success(request, 'Property Record Saved')

    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#prop")

def address_search(request):
# Fetch search parameters from GET request
    parcel = request.GET.get('parcel', '')
    state = request.GET.get('state', '')
    county = request.GET.get('county', '')
    house = request.GET.get('house', '')
    street = request.GET.get('street', '')
    sttype = request.GET.get('sttype', '')

    # Query the database using Q objects
    address = Property.objects.all()
    if parcel:
        address = address.filter(parcel__icontains=parcel)
    if state:
        address = address.filter(state__icontains=state)
    if county:
        address = address.filter(county__icontains=county)
    if house:
        address = address.filter(house_number__icontains=house)
    if street:
        address = address.filter(road_name__icontains=street)
    if sttype:
        address = address.filter(road_type__icontains=sttype)

    # Return results as JSON
    results = list(address.values('id', 'state','county','parcel', 'house_number', 'road_name', 'road_type','direction','apt_unit','extention','city','zip_code'))
    return JsonResponse({'address': results})

def fcl_add_property(request):
    if request.method == 'POST':
        update = request.POST.get('caseid')
        add_prop = request.POST.get('property_id')
        fclinstance = Foreclosure.objects.get(pk=update)
        propinstance = Property.objects.get(pk=add_prop)
        fclinstance.property.add(propinstance)
        messages.success(request,'Property successfully added to current foreclosure')

    #return HttpResponseRedirect(f"/foreclosures/?g_caseid={selected}")
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={update}#prop")
#------------------property-------------End