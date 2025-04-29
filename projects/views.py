from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.contrib import messages
from datetime import timedelta

# -----------Forms------------------
from .forms import *
from propertydata.forms import *
# -----------Models------------------
from . models import *
from realestate_directory.models import *
from propertydata.models import *
# -----------Resources---------------
from .resources import *

imported_data_cache = None


# --------------------------------------------------------------------------------

# Views for Section (Foreclosure)--------------------Start
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

    results = list(foreclosure.values('id', 'state', 'county', 'case_number', 'sale_date', 'sale_type', 'sale_status'))
    return JsonResponse({'foreclosure': results})

def update_foreclosure(request):
    current_user = request.user
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
        fcl_instance.update_possible_surplus()
    
    else:
        fcl_instance = Foreclosure(
            state=state,
            county=county,
            case_number=case,
            sale_type=sale_type,
            sale_status=sale_status,
            case_search_status="Pending",
            changed_at=now()
            )
        
    fcl_instance.save()
    if sel_fcl:
        messages.success(request, 'Foreclosure Instance Updated Successfully!!')
    else:
        messages.success(request, 'New Foreclosure Instance Created!!')
    sel_fcl = fcl_instance.pk

    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={sel_fcl}")

##-------------------------------------Defendant Section
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
    business = request.GET.get('business_def', '')
    designation = request.GET.get('designation_def', '')
    
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
        def_instance = get_object_or_404(Contact,pk=defendant)
        if request.POST.get('delete') == "Delete":
            foreclosure_instance = Foreclosure.objects.get(pk=foreclosure)
            foreclosure_instance.defendant.remove(def_instance)
            messages.success(request, "Defendant Removed")
        elif request.POST.get('update') == "Update":
            prefix = request.POST.get('u_prefix')
            first = request.POST.get('u_first')
            middle = request.POST.get('u_middle')
            last = request.POST.get('u_last')
            suffix = request.POST.get('u_suffix')
            business = request.POST.get('u_business_name')
            designation = request.POST.get('u_designation')
        
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

##-------------------------------------Plaintiff Section
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
        plaintiff = request.POST.get('plt-id')
        plt_instance = get_object_or_404(ForeclosingEntity,pk=plaintiff)
        contact_nm = request.POST.get('u_contact')
        business_nm = request.POST.get('u_business')
        dba = request.POST.get('u_dba')
        if request.POST.get('delete') == "Delete":
            foreclosure_instance = Foreclosure.objects.get(pk=foreclosure)
            foreclosure_instance.plaintiff.remove(plt_instance)
            messages.info(request, "Plaintiff Removed")
        elif request.POST.get('update') == "Update":
            plt_instance.individual_name = contact_nm
            plt_instance.business_name = business_nm
            plt_instance.dba = dba
            plt_instance.save()
            messages.info(request, "Plaintiff Updated")
    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#plt")

def add_plaintiff(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
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
    
    plaintiff = ForeclosingEntity.objects.all()
    if business:
        plaintiff = plaintiff.filter(business_name__icontains=business)
    if dba:
        plaintiff = plaintiff.filter(dba__icontains=dba)
    if contact:
        plaintiff = plaintiff.filter(individual_name__icontains=contact)
    
    pltresults = list(plaintiff.values('id','business_name', 'dba','individual_name'))
    return JsonResponse({'plaintiff': pltresults})

##--------------------------------------Property Section
def search_create_property(request):
    if request.method == 'POST':
        foreclosure = request.POST.get('caseid')
        contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
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
        if related_contact:
            url = f"/skiptrace/?con_id={contact.pk}&related_contact={related_contact}"
        else:
            url = f"/skiptrace/?con_id={contact.pk}"
        return HttpResponseRedirect(url)

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
            if request.POST.get('delete') == "Delete":
                foreclosure_instance = Foreclosure.objects.get(pk=foreclosure)
                foreclosure_instance.property.remove(property_instance)
                messages.info(request, 'Property Record Removed')
            elif request.POST.get('update') == "Update":
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
                messages.info(request, 'Property Record Saved')

    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={foreclosure}#prop")

def address_search(request):

    parcel = request.GET.get('parcel', '')
    state = request.GET.get('state', '')
    county = request.GET.get('county', '')
    house = request.GET.get('house', '')
    street = request.GET.get('street', '')
    sttype = request.GET.get('sttype', '')

    if not any([parcel, state, county, house, street, sttype]):
        address = Property.objects.all()[:0]
    else:
        address = Property.objects.all()
    #address = Property.objects.all()
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

    return HttpResponseRedirect(f"/add_edit_foreclosure/?fcl_id={update}#prop")

# --------------------------------------------------------------------------------

# Views for Section (Skiptracing Checklist)--------------------Start
def skiptracing_checklist(request):
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

# --------------------------------------------------------------------------------

# Views for Section (Skiptracing)--------------------Start
def skiptrace(request):
    researcher = request.user.groups.filter(name="researcher").exists()
    all_contact = Contact.objects.all().distinct()
    
    
    if request.method == 'POST':
        contact_selected = request.POST.get('con_id','')
        related_contact = request.POST.get('related_contact','')
    else:
        contact_selected = request.GET.get('con_id','')
        related_contact = request.GET.get('related_contact','')
    if contact_selected:
        current_con_instance = get_object_or_404(Contact, pk=contact_selected)
        all_mailing = current_con_instance.mailing_address.all()
        all_email = current_con_instance.emails.all()
        all_wireless = current_con_instance.wireless.all()
        all_landline = current_con_instance.landline.all()
        all_related_contact = current_con_instance.related_contacts.all()
        
    else:
        current_con_instance = None
        all_mailing = None
        all_email = None
        all_wireless = None
        all_landline = None
        all_related_contact = None
        


    context = {
        'all_contact':all_contact,
        'contact_selected':contact_selected,
        'current_con_instance':current_con_instance,
        'all_mailing':all_mailing,
        'all_email':all_email,
        'all_wireless':all_wireless,
        'all_landline':all_landline,
        'all_related_contact':all_related_contact,
        'researcher':researcher,
        'related_contact':related_contact,
    }
    return render(request,'projects/skiptrace.html', context)

def mark_as_skiptraced(request):
    selected_contact = request.POST.get('related_contact') #reversed contact instance to current contact
    related_contact = request.POST.get('con_id')#10-skiptrace
    related_contact_instance = Contact.objects.get(pk=related_contact)
    
    related_contact_instance.skiptraced = True
    related_contact_instance.skiptrace_comment = "Done"
    related_contact_instance.save()
    return HttpResponseRedirect(f"/skiptrace/?con_id={selected_contact if selected_contact else related_contact}#rc")

@csrf_exempt  # Add this only if CSRF tokens are not used. Otherwise, use the CSRF token in your AJAX request.
def saveskiptraceComment(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            
            con_id = data.get('id')          
            # Fetch the corresponding event object from the database
            con_instance = Contact.objects.get(id=con_id)
            
            # Update the fields
            if con_instance.skiptrace_comment == "Not Found":
                con_instance.skiptraced = False
                con_instance.save()
            else:
                try:
                    con_instance.skiptrace_comment = "Not Found"
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
                con_instance.save()
           
            return JsonResponse({'status': 'success', 'message': 'Row updated successfully!'})

        except Contact.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Contact not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Respond with an error if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def CreateUpdateContact(request):
    contact_selected = request.POST.get('con_id','')
    related_contact = request.POST.get('related_contact')
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
    if related_contact:
        url = f"/skiptrace/?con_id={contact_selected}&related_contact={related_contact}"
    else:
        url = f"/skiptrace/?con_id={contact_selected}"
    return redirect(url)

def filter_contact(request):
        prefix = request.GET.get('prefix','')
        firstname = request.GET.get('f_name','')
        middlename = request.GET.get('m_name','')
        lastname = request.GET.get('l_name','')
        suffix = request.GET.get('suffix','')
        business = request.GET.get('b_name','')
        designation = request.GET.get('b_desig','')
        
        if not any([prefix, firstname, middlename, lastname, suffix, business, designation]):
            contact = Contact.objects.all()[:0]
        else:
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
        if designation:
            contact = contact.filter(designation__icontains=designation)

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
        
        return JsonResponse({'contact': results})

#---------------------------------------------------Mailing Address Section

def fetch_mailing_address(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    contact_instance = Contact.objects.get(pk=selected_contact)
    foreclosures = Foreclosure.objects.filter(defendant=contact_instance)
    for fcl in foreclosures:
        properties = fcl.property.all()
        for prop in properties:
            property_instance = Property.objects.get(pk=prop.pk)
            contact_instance.mailing_address.add(property_instance)
    messages.info(request, 'Successfully Fetched All Mailing Addresses')
    if related_contact:
        url = f"/skiptrace/?con_id={contact_instance.pk}&related_contact={related_contact}#mailing_address"
    else:
        url = f"/skiptrace/?con_id={contact_instance.pk}#mailing_address"
    return HttpResponseRedirect(url)

def update_contact(request):
    if request.method == 'POST':
    
        contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
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
            if request.POST.get("update") == "Update":
                property_instance.save()
                messages.success(request, 'Property Record Saved')
            elif request.POST.get("delete") == "Delete":
                contact_instance = Contact.objects.get(pk=contact)
                contact_instance.mailing_address.remove(property_instance)
                messages.success(request, 'Property Record Removed')
        if related_contact:
            url = f"/skiptrace/?con_id={contact}&related_contact={related_contact}"
        else:
            url = f"/skiptrace/?con_id={contact}"
    return HttpResponseRedirect(url)

    #Mailing Address Section-------------------------End

def addMailing(request):
    if request.method == 'POST':
        update = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
        add_prop = request.POST.get('property_id')
        coninstance = Contact.objects.get(pk=update)
        propinstance = Property.objects.get(pk=add_prop)
        coninstance.mailing_address.add(propinstance)
        messages.success(request,'Mailing Address successfully added to current contact')
        if related_contact:
            url = f"/skiptrace/?con_id={update}&related_contact={related_contact}"
        else:
            url = f"/skiptrace/?con_id={update}"
    return HttpResponseRedirect(url)

# ---------Note------ search_create_property view is used to search and create mailing address

#---------------------------------------------------Email Section
def update_email(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        
        related_contact = request.POST.get('related_contact')
        email = request.POST.get('email_id')
        if email:
            emailinstance = Email.objects.get(pk=email)
            contact_instance = Contact.objects.get(pk=contact)
            if request.POST.get('delete') == "Delete":
                contact_instance.emails.remove(emailinstance)
                messages.info(request, "Email Removed!")
            elif request.POST.get('update') == "Update":
                emailinstance.email_address = request.POST.get('email')
                emailinstance.save()
                messages.info(request, "Email Saved!")
        if related_contact:
            url = f"/skiptrace/?con_id={contact}&related_contact={related_contact}#em"
        else:
            url = f"/skiptrace/?con_id={contact}#em"
    return redirect(url)

def search_create_email(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
        emailaddress = request.POST.get('email')
        createEmail = Email(email_address = emailaddress)
        createEmail.save()
        messages.success(request,'New Email Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.emails.add(createEmail)
            messages.info(request, 'Email added to current contact instance')
        if related_contact:
            url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#em"
        else:
            url = f"/skiptrace/?con_id={contactinstance.pk}#em"
    return redirect(url)

def filterEmail(request):
    emailaddress = request.GET.get('email')

    emails = Email.objects.all()
    if emailaddress:
        emails = emails.filter(email_address__icontains=emailaddress)
    else:
        emails = Email.objects.all()[:0]
    results = list(emails.values('id', 'email_address'))
    return JsonResponse({'emails':results})

def add_email(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    emailid = request.POST.get('email_id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        emailinstance = Email.objects.get(pk=emailid)
        contactinstance.emails.add(emailinstance)
        messages.info(request,'Email added to contact')
    if related_contact:
            url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#em"
    else:
        url = f"/skiptrace/?con_id={contactinstance.pk}#em"
    return redirect(url)
    
#---------------------------------------------------Wireless Section
def update_wireless(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        related_contact = request.POST.get('related_contact')
        wireless = request.POST.get('wireless-id')
        if wireless:
            w_instance = Wireless_Number.objects.get(pk=wireless)
            contact_instance = Contact.objects.get(pk=contact)
            if request.POST.get('delete') == "Delete":
                contact_instance.wireless.remove(w_instance)
                messages.info(request, "Number Removed!")
            elif request.POST.get('update') == "Update":
                w_instance.w_number = request.POST.get('wireless')
                w_instance.save()
                messages.info(request, "Number Updated!")
        if related_contact:
            url = f"/skiptrace/?con_id={contact}&related_contact={related_contact}#wn"
        else:
            url = f"/skiptrace/?con_id={contact}#wn"
    return redirect(url)

def create_wireless(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
        wNumber = request.POST.get('wireless')
        createwireless = Wireless_Number(w_number = wNumber)
        createwireless.save()
        messages.success(request,'New Wireless Number Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.wireless.add(createwireless)
            messages.info(request, 'Wireless Number added to current contact instance')
        if related_contact:
            url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#wn"
        else:
            url = f"/skiptrace/?con_id={contactinstance.pk}#wn"
    return redirect(url)

def filterWireless(request):
    w_number = request.GET.get('wireless')
    wireless = Wireless_Number.objects.all()
    if w_number:
        wireless = wireless.filter(w_number__icontains=w_number)
    else:
        wireless = Wireless_Number.objects.all()[:0]
    results = list(wireless.values('id', 'w_number'))
    return JsonResponse({'wireless':results})

def add_wireless(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    w_id = request.POST.get('wireless-id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        w_instance = Wireless_Number.objects.get(pk=w_id)
        contactinstance.wireless.add(w_instance)
        messages.info(request,'Wireless number added to contact')
    if related_contact:
        url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#wn"
    else:
        url = f"/skiptrace/?con_id={contactinstance.pk}#wn"
    return redirect(url)

#---------------------------------------------------Landline Section
def updateLandline(request):
    if request.method == 'POST':
        contact = request.POST.get('con_id','')
        related_contact = request.POST.get('related_contact')
        landline = request.POST.get('landline-id')
        if landline:
            l_instance = Landline_Number.objects.get(pk=landline)
            contact_instance = Contact.objects.get(pk=contact)
            if request.POST.get('delete') == "Delete":
                contact_instance.landline.remove(l_instance)
                messages.info(request, "Number Removed!")
            elif request.POST.get('update') == "Update":
                l_instance.l_number = request.POST.get('landline')
                l_instance.save()
                messages.info(request, "Landline Number Updated!")
        if related_contact:
            url = f"/skiptrace/?con_id={contact}&related_contact={related_contact}#ln"
        else:
            url = f"/skiptrace/?con_id={contact}#ln"
    return redirect(url)

def createLandline(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
        lNumber = request.POST.get('landline')
        createlandline = Landline_Number(l_number = lNumber)
        createlandline.save()
        messages.success(request,'New Landline Number Instance Created')
        if selected_contact:
            contactinstance = Contact.objects.get(pk=selected_contact)
            contactinstance.landline.add(createlandline)
            messages.info(request, 'Landline Number added to current contact instance')
        if related_contact:
            url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#ln"
        else:
            url = f"/skiptrace/?con_id={contactinstance.pk}#ln"
    return redirect(url)

def filterLandline(request):
    l_number = request.GET.get('landline')
    landline = Landline_Number.objects.all()
    if l_number:
        landline = landline.filter(l_number__icontains=l_number)
    else:
        landline = Landline_Number.objects.all()[:0]
    results = list(landline.values('id', 'l_number'))
    return JsonResponse({'landline':results})

def addLandline(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    l_id = request.POST.get('landline-id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        l_instance = Landline_Number.objects.get(pk=l_id)
        contactinstance.landline.add(l_instance)
        messages.info(request,'Landline number added to contact')
    if related_contact:
        url = f"/skiptrace/?con_id={contactinstance.pk}&related_contact={related_contact}#ln"
    else:
        url = f"/skiptrace/?con_id={contactinstance.pk}#ln"
    return redirect(url)

#---------------------------------------------------Related Contact Section
def filter_related_contact(request):
    prefix = request.GET.get('rc_prefix','')
    firstname = request.GET.get('rc_first','')
    middlename = request.GET.get('rc_middle','')
    lastname = request.GET.get('rc_last','')
    suffix = request.GET.get('rc_suffix','')
    otherquery = request.GET.get('search_query','')
    
    if not any([prefix, firstname, middlename, lastname, suffix, otherquery]):
        contact = Contact.objects.all()[:0]
    else:
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
    if otherquery:
        if len(contact.filter(business_name__icontains=otherquery)) > 0:
            contact = contact.filter(business_name__icontains=otherquery)
        # elif contact.filter(business_name__icontains=otherquery).count > 0:
    
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
    
    return JsonResponse({'rc_contact': results})

def create_related_contact(request):
    if request.method == 'POST':
        selected_contact = request.POST.get('con_id')
        related_contact = request.POST.get('related_contact')
        prefix = request.POST.get('rc_prefix')
        fname = request.POST.get('rc_first')
        mname = request.POST.get('rc_middle')
        lname = request.POST.get('rc_last')
        suffix = request.POST.get('rc_suffix')
        createcontact = Contact(
            name_prefix = prefix,
            first_name = fname,
            middle_name = mname,
            last_name = lname,
            name_suffix = suffix
            )
        createcontact.save()
        messages.success(request,'New Contact Instance Created')
        if selected_contact:
            selectedcontactinstance = Contact.objects.get(pk=selected_contact)
            selectedcontactinstance.related_contacts.add(createcontact)
            messages.info(request, 'Contact Added as Related Contact')
            if related_contact:
                url = f"/skiptrace/?con_id={selectedcontactinstance.pk}&related_contact={related_contact}#rc"
            else:
                url = f"/skiptrace/?con_id={selectedcontactinstance.pk}#rc"
    return HttpResponseRedirect(url)

def add_related_contact(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    rc_id = request.POST.get('add_rc_id')
    if selected_contact:
        contactinstance = Contact.objects.get(pk=selected_contact)
        add_rc_instance = Contact.objects.get(pk=rc_id)
        contactinstance.related_contacts.add(add_rc_instance)
        messages.info(request,'Related Contact Added')
    if related_contact:
        url = f"/skiptrace/?con_id={selected_contact}&related_contact={related_contact}#rc"
    else:
        url = f"/skiptrace/?con_id={selected_contact}#rc"
    return HttpResponseRedirect(url)

def skiptrace_related_contact(request):
    selected_contact = request.POST.get('con_id')
    related_contact = request.POST.get('related_contact')
    if request.POST.get('delete') == "Delete":
        contact_instance = Contact.objects.get(pk=related_contact)
        related_instance = Contact.objects.get(pk=selected_contact)
        contact_instance.related_contacts.remove(related_instance)
        messages.info(request, "Related Contact Instance Removed!")
        url = f"/skiptrace/?con_id={related_contact}"
    elif request.POST.get('skiptrace') == "Edit" or "Skiptrace":
        url = f"/skiptrace/?con_id={selected_contact}&related_contact={related_contact}"
    return redirect(url)

# --------------------------------------------------------------------------------

# Views for Section (Delivered Tasks)--------------------Start
def deliveredtasks(request):
    current_user=request.user
    p=Paginator(Foreclosure.objects.filter(case_search_assigned_to=current_user, case_search_status = "Completed"), 20)

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

# --------------------------------------------------------------------------------